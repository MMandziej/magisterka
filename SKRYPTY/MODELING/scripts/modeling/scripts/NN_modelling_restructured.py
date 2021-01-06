"""
Created on Fri Mar 20 15:55:27 2020

Functions used to iteratively test different models with randomly assigned
parameteres values and choose the ones that met set criteria. Model fitting
at first stage is done on full dataset with all columns and on selected columns
only at the second stage.
"""

import numpy as np
import os
import pandas as pd
import random
import time

from datetime import date
from keras import losses, optimizers
from keras.layers import Activation, Dense

from sklearn.metrics import roc_auc_score
from sklearn.utils import class_weight

from tensorflow import keras
from tensorflow.keras import backend as K, metrics, layers, losses, optimizers

from tensorflow.keras.activations import elu, exponential, hard_sigmoid, linear, \
    relu, sigmoid, softmax, tanh
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dropout, Dense
from tensorflow.keras.losses import binary_crossentropy, categorical_crossentropy, \
    logcosh, mean_squared_error, poisson, mean_absolute_error
from tensorflow.keras.optimizers import Adadelta, Adam, Nadam, RMSprop, SGD


def full_search(train_data: pd.DataFrame,
                train_features: list,
                test_data: pd.DataFrame,
				train_labels: list,
                test_labels: list,
                max_iter=100,
                max_hours=5,
                min_auc=0.6,
                max_overfit_auc=0.03,
                prefix='') -> list:
    """ Performs initial search for promising model types (neural networks)
    that are later to be optimized. Modelling is based on a basis of
    random search - random model parameters are choosen.
    Models with the best AUC metric and acceptable overfit are saved and stored
    Models are fitted in a while loop until maximum number of iterations or
    set elapse time is reached.
    After that results are exported to desired location.


    Parameters
    ----------
    train_data : pd.DataFrame
        tabular data with data to fit model on
    train_features : list
        list of features (independent variables) to be included in the model
        bar from label (output variable)
    test_data : pd.DataFrame
        tabular data with data to evaluate model performance on
	train_labels : list (of str values)
        array-like values of output variable
	test_labels : list (of str values)
        array-like values of output variable
    columns_to_drop : list
        list of features to remove from dataset (selected features may
        give better results than complete list)
    max_iter : int
        stopping criterium in while loop - number of iterations for which
        different model classes will be generated
    max_hours : float
        stopping criterium in while loop (models will generated for that
        number of hours)
    target : str
        label - output variable
    min_auc : float
        minimum AUC with which model will be accepted
    max_overfit_auc : float
        maximum allowed overfit between train and test AUC
    prefix : str
        guid with which to export results (best models) to pointed location

    Returns
    -------
    models_list : list
        list of models that met the criteria of AUC and overfit (tensorflow
        objects)
    best_models_list : list
        list of model parametrs that met the criteria of AUC and overfit
    result_df : pd.DataFrame
        tabular results of all generated models with their parameters, metrics
    """
    # create output export directory if it doesn't exist
    os.getcwd()
    if not os.path.exists('model_training/results/nn'):
        os.makedirs('model_training/results/nn')
    export_path = r'model_training/results/nn/'

    # declare possible parameter values for random search
    lr = np.arange(0.005, 0.1, 0.005)
    batch_size = np.arange(20, 110, 10)
    units = [16, 32, 64, 128, 256, 512]
    num_hidden_layers = [1, 2, 3, 4, 5, 6]
    epochs = [100, 150, 200]
    dropout = np.arange(0.05, 0.2, 0.05)
    optimizers = [Adam, SGD]  # Nadam, RMSprop,
    losses = ['binary_crossentropy']  # 'logcosh', 'mean_absolute_error', 'poisson', 'mean_squared_error'
    activation = [relu, tanh, elu]  # ,exponential
    last_activations = [sigmoid]
    early_stop = EarlyStopping(monitor='val_loss',
                               min_delta=0.03,
                               patience=30,
                               verbose=0,
                               mode='min',
                               restore_best_weights=True)

    # adjust class weights to make sure 0 and 1 classes are treated equally as
    # usually there is a scarcity of ones
    class_weights = dict(enumerate(
        class_weight.compute_class_weight('balanced',
                                          np.unique(test_labels),
                                          test_labels)))

    # create baselinemodel with all columns
    # initialize lists to append with model results

    results = []
    models_list = []
    models_params = []
    best_auc_test = 0
    best_models = []
    execution_time = 0
    i = 0
    start_time = time.time()
    while (execution_time < max_hours) and i != max_iter:
        # define parameters range to perform random search
        curr_num_hidden_layers = num_hidden_layers[random.randrange(
            0, len(num_hidden_layers), 1)]
        last_activation = last_activations[random.randrange(
            0, len(last_activations), 1)]
        loss_function = losses[random.randrange(0, len(losses), 1)]
        optimizer_function = optimizers[random.randrange(
            0, len(optimizers), 1)]
        current_lr = lr[random.randrange(0, len(lr), 1)]
        current_epoch = epochs[random.randrange(0, len(epochs), 1)]
        current_batch_size = batch_size[random.randrange(
            0, len(batch_size), 1)]
        current_dropout = dropout[random.randrange(0, len(dropout), 1)]

        random.seed()
        model = Sequential()
        model.add(Dense(units[random.randrange(0, len(units), 1)],
                  input_dim=train_data.shape[1],
                  activation=activation[random.randrange(0, len(activation), 1)]))
        for j in range(curr_num_hidden_layers):
            model.add(Dropout(current_dropout))
            model.add(Dense(units[random.randrange(0, len(units), 1)],
                            activation=activation[random.randrange(0, len(activation), 1)]))

        model.add(Dense(1, activation=last_activation,
                        kernel_initializer='normal'))

        # define avaluation and optimization criteria
        model.compile(loss=loss_function,
                      optimizer=optimizer_function(lr=current_lr),
                      metrics=['acc'])

        history = model.fit(train_data,
                            train_features,
                            epochs=current_epoch,
                            batch_size=current_batch_size,
                            validation_split=0.2,
                            verbose=0,
                            callbacks=[early_stop],
                            class_weight=class_weights)

        train_predictions = model.predict(train_data)
        test_predictions = model.predict(test_data)
        
        predictions_df_train = pd.DataFrame(train_predictions, columns=['Score'])
        predictions_df_test = pd.DataFrame(test_predictions, columns=['Score'])

        # calculate [%] of errors detected in 75% population - train data
        train_results = pd.concat([predictions_df_train, train_labels], axis=1)
        train_results = train_results.sort_values(by='Score', axis=0, ascending=False)
        len_train_75 = round(len(train_results) * 0.75)
        positives_train = train_results['Label'].sum()
        positives_train_75 = train_results.iloc[:len_train_75]['Label'].sum()
        ratio_train75 = positives_train_75 / positives_train

        # calculate [%] of errors detected in 75% population - test data
        test_results = pd.concat([predictions_df_test, test_labels], axis=1)
        test_results = test_results.sort_values(by='Score', axis=0, ascending=False)
        len_test_75 = round(len(test_results) * 0.75)
        positives_test = test_results['Label'].sum()
        positives_test_75 = test_results.iloc[:len_test_75]['Label'].sum()
        ratio_test75 = positives_test_75 / positives_test
        
        auc_test = roc_auc_score(test_labels, predictions_df_test)
        auc_train = roc_auc_score(train_features, predictions_df_train)      

        # for regression use val loss
        # auc = min(history.history['val_loss'])

        model_params = {'lr': current_lr,
                        'batch_size': current_batch_size,
                        'model_layers': model.get_config(),
                        'epochs': current_epoch,
                        'dropout': current_dropout,
                        'optimizer': str(optimizer_function),
                        'losses': loss_function,
                        'auc_train': auc_train,
                        'auc_test': auc_test,
                        'overfit': round((auc_train - auc_test), 3),
                        'train_errors_75': ratio_train75,
                        'test_errors_75': ratio_test75,
                        'columns_used': test_data.columns.to_list()}
        # append results table with the latest model parameters and metrics
        results.append(model_params)

        if (auc_test > min_auc) and (auc_train - auc_test) < max_overfit_auc and (auc_train - auc_test) > -0.015:
            models_list.append(model)
            models_params.append(model_params)
            if auc_test > best_auc_test:
                best_auc_test = auc_test
                best_models.append(model)
        # else:
        #    models_list.append(np.nan)
        K.clear_session()
        i = i + 1
        execution_time = (time.time() - start_time) / 3600
        print("Iteration: {}. Time elapsed: {}".format(str(i), round(execution_time, 4)))
        print(auc_train, auc_test)

    results_df = pd.DataFrame(models_params)
    results_df.to_csv(export_path + str(prefix) + str(date.today()) + '.csv')

    if best_models:
        best_models[-1].save(export_path + str(prefix) + str(date.today()) +
                    '.h5')
    return models_list, models_params, results_df


def narrow_search(train_data: pd.DataFrame,
                  train_features: list,
                  test_data: pd.DataFrame,
				  train_labels: list,
                  test_labels: list,
                  columns_to_drop=None,
                  max_iter=100,
                  max_hours=5,
                  min_auc=0.6,
                  max_overfit_auc=0.03,
                  prefix='') -> list:
    """ Performs second search in order to optimize the features of the
    dataset and find the list of columns for which results are the best.
    Feature are dropped from dataset in a loop.
    Modelling is based on a basis of random search - random model parameters
    are choosen.
    Models with the best AUC metric and acceptable overfit are saved and stored
    Models are fitted in a while loop until maximum number of iterations or
    set elapse time is reached.
    After that results are exported to desired location.


    Parameters
    ----------
    train_data : pd.DataFrame
        tabular data with data to fit model on
    train_features : list
        list of features (independent variables) to be included in the model
        bar from label (output variable)
    test_data : pd.DataFrame
        tabular data with data to evaluate model performance on
    train_labels : list (of str values)
        array-like values of output variable
    test_labels : list (of str values)
        array-like values of output variable
    columns_to_drop : list
        list of features to remove from dataset (selected features may
        give better results than complete list)
    max_iter : int
        stopping criterium in while loop - number of iterations for which
        different model classes will be generated
    max_hours : float
        stopping criterium in while loop (models will generated for that
        number of hours)
    target : str
        label - output variable
    min_auc : float
        minimum AUC with which model will be accepted
    max_overfit_auc : float
        maximum allowed overfit between train and test AUC
    prefix : str
        guid with which to export results (best models) to pointed location

    Returns
    -------
    models_list : list
        list of models that met the criteria of AUC and overfit (tensorflow
        objects)
    best_models_list : list
        list of model parametrs that met the criteria of AUC and overfit
    result_df : pd.DataFrame
        tabular results of all generated models with their parameters, metrics
    """
    # create output export directory if it doesn't exist
    os.getcwd()
    if not os.path.exists('model_training/results/nn'):
        os.makedirs('model_training/results/nn')
    export_path = r'model_training/results/nn/'

    # declare possible parameter values for narrow search
    lr = np.arange(0.005, 0.1, 0.005)
    batch_size = np.arange(20, 110, 10)
    units = [16, 32, 64, 128, 256]
    num_hidden_layers = [1, 2, 3, 4, 5, 6]
    epochs = [100, 150, 200]
    dropout = np.arange(0.1, 0.3, 0.05)
    optimizers = [Adam, SGD]  # Nadam, RMSprop,
    losses = ['binary_crossentropy']  # 'logcosh','mean_absolute_error' ,'poisson','mean_squared_error'
    activation = [relu, tanh, elu]  # ,exponential
    last_activations = [sigmoid]
    early_stop = EarlyStopping(monitor='val_loss',
                               min_delta=0.03,
                               patience=20,
                               verbose=0,
                               mode='min',
                               restore_best_weights=True)

    # adjust class weights to make sure 0 and 1 classes are treated equally as usually there is a scarcity of ones
    class_weights = dict(enumerate(
        class_weight.compute_class_weight('balanced',
                                          np.unique(test_labels),
                                          test_labels)))
    if columns_to_drop is None:
        columns_to_drop = train_data.columns.to_list()

    # create empty list to append with selected cols models
    max_global_auc = 0
    best_models_list_params = []
    best_models_list_h5 = []
    # try models on trimmed dataset
    for c in range(len(columns_to_drop)):
        max_auc = 0
        best_models_local_params = []
        best_models_local_h5 = []
        models_list = []
        temp_train_data = train_data.drop([columns_to_drop[c]], axis=1)
        temp_test_data = test_data.drop([columns_to_drop[c]], axis=1)

        i = 0
        iteration_start_time = time.time()
        execution_time = 0
        while (execution_time < max_hours) and i != max_iter:
            curr_num_hidden_layers = num_hidden_layers[random.randrange(
                0, len(num_hidden_layers), 1)]
            last_activation = last_activations[random.randrange(
                0, len(last_activations), 1)]
            loss_function = losses[random.randrange(0, len(losses), 1)]
            optimizer_function = optimizers[random.randrange(
                0, len(optimizers), 1)]
            current_lr = lr[random.randrange(0, len(lr), 1)]
            current_epoch = epochs[random.randrange(0, len(epochs), 1)]
            current_batch_size = batch_size[random.randrange(
                0, len(batch_size), 1)]
            current_dropout = dropout[random.randrange(0, len(dropout), 1)]

            random.seed()
            model = Sequential()
            model.add(Dense(units[random.randrange(0, len(units), 1)],
                            input_dim=temp_train_data.shape[1],
                            activation=activation[random.randrange(0, len(activation), 1)]))

            for j in range(curr_num_hidden_layers):
                model.add(Dropout(current_dropout))
                model.add(Dense(units[random.randrange(0, len(units), 1)],
                                activation=activation[random.randrange(0, len(activation), 1)]))

            model.add(Dense(1,
                            activation=last_activation,
                            kernel_initializer='normal'))
            model.compile(loss=loss_function,
                          optimizer=optimizer_function(lr=current_lr),
                          metrics=['acc'])
            history = model.fit(temp_train_data,
                                train_features,
                                epochs=current_epoch,
                                batch_size=current_batch_size,
                                validation_split=0.2,
                                verbose=0,
                                callbacks=[early_stop],
                                class_weight=class_weights)

            train_predictions = model.predict(temp_train_data)
            test_predictions = model.predict(temp_test_data)

            predictions_df_train = pd.DataFrame(train_predictions, columns=['Score'])
            predictions_df_test = pd.DataFrame(test_predictions, columns=['Score'])
    
            # calculate [%] of errors detected in 75% population - train data
            train_results = pd.concat([predictions_df_train, train_labels], axis=1)
            train_results = train_results.sort_values(by='Score', axis=0, ascending=False)
            len_train_75 = round(len(train_results) * 0.75)
            positives_train = train_results['Label'].sum()
            positives_train_75 = train_results.iloc[:len_train_75]['Label'].sum()
            ratio_train75 = positives_train_75 / positives_train
    
            # calculate [%] of errors detected in 75% population - test data
            test_results = pd.concat([predictions_df_test, test_labels], axis=1)
            test_results = test_results.sort_values(by='Score', axis=0, ascending=False)
            len_test_75 = round(len(test_results) * 0.75)
            positives_test = test_results['Label'].sum()
            positives_test_75 = test_results.iloc[:len_test_75]['Label'].sum()
            ratio_test75 = positives_test_75 / positives_test
            
            auc_test = roc_auc_score(test_labels, predictions_df_test)
            auc_train = roc_auc_score(train_features, predictions_df_train)
            # for regression use val loss
            # auc = min(history.history['val_loss'])

            model_params = {'lr': current_lr,
                            'batch_size': current_batch_size,
                            'model_layers': model.get_config(),
                            'epochs': current_epoch,
                            'dropout': current_dropout,
                            'optimizer': str(optimizer_function),
                            'losses': loss_function,
                            'auc_train': auc_train,
                            'auc_test': auc_test,
                            'overfit': round((auc_train - auc_test), 3),
                            'train_errors_75': ratio_train75,
                            'test_errors_75': ratio_test75,
                            'columns_used': temp_test_data.columns.to_list()}

            if (auc_test > min_auc) and (auc_train - auc_test) < max_overfit_auc and (auc_train - auc_test) > -0.015:
                models_list.append(model)
                # append list with the best model on local search (current column selection)
                if auc_test > max_auc:
                    best_models_local_h5.append(model)
                    best_models_local_params.append(model_params)
                    max_auc = auc_test
            else:
                models_list.append(np.nan)
            K.clear_session()
            i = i + 1
            execution_time = (time.time() - iteration_start_time) / 3600
            print("Narrow search. Iteration: {}. Time elapsed {}. \
                  Column dropped: {}. Layer: {}. AUC train: {}. AUC test: {}.".format(
                  str(i), execution_time, str(c), str(j), str(auc_train), str(auc_test)))

        # append best models with the best model from current columns selection
        if best_models_local_h5:
            best_models_list_h5.append(best_models_local_h5[-1])
            best_models_list_params.append(best_models_local_params[-1])
            # export best model on current column selection
            best_models_local_h5[-1].save(export_path + str(prefix) +
                                          str(c) + '.h5')
            # if the best auc score was improved change dataset columns to the current ones
            if best_models_local_params[-1]['auc_test'] > max_global_auc:
                test_data = temp_test_data
                train_data = temp_train_data
                max_global_auc = best_models_local_params[-1]['auc_test']

    # export parameters of best models of each columns selections
    best_models_results_df = pd.DataFrame(best_models_list_params)
    best_models_results_df.to_csv(export_path + str(prefix) + '_' +
                                  str(date.today()) + '.csv',
                                  index=False)
    return best_models_list_h5, best_models_list_params, best_models_results_df


def backward_search(train_data: pd.DataFrame,
                    train_features: list,
                    test_data: pd.DataFrame,
                    test_labels: list,
                    columns_to_drop=None,
                    max_iter=100,
                    max_hours=5,
                    min_auc=0.6,
                    max_overfit_auc=0.03,
                    prefix='') -> list:
    """ Performs second search in order to optimize the features of the
    dataset and find the list of columns for which results are the best.
    Feature are dropped from dataset in a loop.
    Modelling is based on a basis of random search - random model parameters
    are choosen.
    Models with the best AUC metric and acceptable overfit are saved and stored
    Models are fitted in a while loop until maximum number of iterations or
    set elapse time is reached.
    After that results are exported to desired location.


    Parameters
    ----------
    train_data : pd.DataFrame
        tabular data with data to fit model on
    train_features : list
        list of features (independent variables) to be included in the model
        bar from label (output variable)
    test_data : pd.DataFrame
        tabular data with data to evaluate model performance on
    test_labels : list (of str values)
        array-like values of output variable
    columns_to_drop : list
        list of features to remove from dataset (selected features may
        give better results than complete list)
    max_iter : int
        stopping criterium in while loop - number of iterations for which
        different model classes will be generated
    max_hours : float
        stopping criterium in while loop (models will generated for that
        number of hours)
    target : str
        label - output variable
    min_auc : float
        minimum AUC with which model will be accepted
    max_overfit_auc : float
        maximum allowed overfit between train and test AUC
    prefix : str
        guid with which to export results (best models) to pointed location

    Returns
    -------
    models_list : list
        list of models that met the criteria of AUC and overfit (tensorflow
        objects)
    best_models_list : list
        list of model parametrs that met the criteria of AUC and overfit
    result_df : pd.DataFrame
        tabular results of all generated models with their parameters, metrics
    """
    # create output export directory if it doesn't exist
    os.getcwd()
    if not os.path.exists('model_training/results/nn'):
        os.makedirs('model_training/results/nn')
    export_path = r'model_training/results/nn/'

    # declare possible parameter values for narrow search
    lr = np.arange(0.005, 0.1, 0.005)
    batch_size = np.arange(20, 110, 10)
    units = [16, 32, 64, 128, 256]
    num_hidden_layers = [1, 2, 3, 4, 5, 6]
    epochs = [100, 150, 200]
    dropout = np.arange(0.1, 0.3, 0.05)
    optimizers = [Adam, SGD]  # Nadam, RMSprop,
    losses = ['binary_crossentropy']  # 'logcosh','mean_absolute_error' ,'poisson','mean_squared_error'
    activation = [relu, tanh, elu]  # ,exponential
    last_activations = [sigmoid]
    early_stop = EarlyStopping(monitor='val_loss',
                               min_delta=0.03,
                               patience=20,
                               verbose=0,
                               mode='min',
                               restore_best_weights=True)

    # adjust class weights to make sure 0 and 1 classes are treated equally as usually there is a scarcity of ones
    class_weights = dict(enumerate(
        class_weight.compute_class_weight('balanced',
                                          np.unique(test_labels),
                                          test_labels)))
    if columns_to_drop is None:
        columns_to_drop = train_data.columns.to_list()

    # create empty list to append with selected cols models
    temp_train_data = train_data
    temp_test_data = test_data
    best_models_list_params = []
    best_models_list_h5 = []
    # try models on trimmed dataset
    for idx, col in enumerate(columns_to_drop):
        max_auc = 0
        best_models_local_params = []
        best_models_local_h5 = []
        models_list = []
        temp_train_data = train_data.drop(col, axis=1)
        temp_test_data = test_data.drop(col, axis=1)

        i = 0
        iteration_start_time = time.time()
        execution_time = 0
        while (execution_time < max_hours) and i != max_iter:
            curr_num_hidden_layers = num_hidden_layers[random.randrange(
                0, len(num_hidden_layers), 1)]
            last_activation = last_activations[random.randrange(
                0, len(last_activations), 1)]
            loss_function = losses[random.randrange(0, len(losses), 1)]
            optimizer_function = optimizers[random.randrange(
                0, len(optimizers), 1)]
            current_lr = lr[random.randrange(0, len(lr), 1)]
            current_epoch = epochs[random.randrange(0, len(epochs), 1)]
            current_batch_size = batch_size[random.randrange(
                0, len(batch_size), 1)]
            current_dropout = dropout[random.randrange(0, len(dropout), 1)]

            random.seed()
            model = Sequential()
            model.add(Dense(units[random.randrange(0, len(units), 1)],
                            input_dim=temp_train_data.shape[1],
                            activation=activation[random.randrange(0, len(activation), 1)]))

            for j in range(curr_num_hidden_layers):
                model.add(Dropout(current_dropout))
                model.add(Dense(units[random.randrange(0, len(units), 1)],
                                activation=activation[random.randrange(0, len(activation), 1)]))

            model.add(Dense(1,
                            activation=last_activation,
                            kernel_initializer='normal'))
            model.compile(loss=loss_function,
                          optimizer=optimizer_function(lr=current_lr),
                          metrics=['acc'])
            history = model.fit(temp_train_data,
                                train_features,
                                epochs=current_epoch,
                                batch_size=current_batch_size,
                                validation_split=0.2,
                                verbose=0,
                                callbacks=[early_stop],
                                class_weight=class_weights)
            test_predictions = model.predict(temp_test_data)
            predictions_df_test = pd.DataFrame(test_predictions)
            train_predictions = model.predict(temp_train_data)
            predictions_df_train = pd.DataFrame(train_predictions)

            auc_test = roc_auc_score(test_labels, predictions_df_test)
            auc_train = roc_auc_score(train_features, predictions_df_train)
            # for regression use val loss
            # auc = min(history.history['val_loss'])

            model_params = {'lr': current_lr,
                            'batch_size': current_batch_size,
                            'model_layers': model.get_config(),
                            'epochs': current_epoch,
                            'dropout': current_dropout,
                            'optimizer': str(optimizer_function),
                            'losses': loss_function,
                            'auc_train': auc_train,
                            'auc_test': auc_test,
                            'overfit': round((auc_train - auc_test), 3),
                            'columns_used': temp_test_data.columns.to_list()}

            if (auc_test > min_auc) and (auc_train - auc_test) < max_overfit_auc and (auc_train - auc_test) > -0.015:
                models_list.append(model)
                # append list with the best model on local search (current column selection)
                if auc_test > max_auc:
                    best_models_local_h5.append(model)
                    best_models_local_params.append(model_params)
                    max_auc = auc_test
            else:
                models_list.append(np.nan)
            K.clear_session()
            i = i + 1
            execution_time = (time.time() - iteration_start_time) / 3600
            print("Backward search. Iteration: {}. Time elapsed {}. \
                  Column dropped: {}. Layer: {}. AUC train: {}. AUC test: {}.".format(
                  str(i), execution_time, str(idx), str(j), str(auc_train), str(auc_test)))

        # append best models with the best model from current columns selection
        if best_models_local_h5:
            best_models_list_h5.append(best_models_local_h5[-1])
            best_models_list_params.append(best_models_local_params[-1])
            # export best model on current column selection
            best_models_local_h5[-1].save(export_path + str(prefix) +
                                          str(idx) + '.h5')

    # export parameters of best models of each columns selections
    best_models_results_df = pd.DataFrame(best_models_list_params)
    best_models_results_df.to_csv(export_path + str(prefix) + '_' +
                                  str(date.today()) + '.csv',
                                  index=False)
    return best_models_list_h5, best_models_list_params, best_models_results_df


def forward_search(train_data: pd.DataFrame,
                   train_features: list,
                   test_data: pd.DataFrame,
                   test_labels: list,
                   columns_to_add=None,
                   max_iter=100,
                   max_hours=5,
                   min_auc=0.6,
                   max_overfit_auc=0.03,
                   prefix='') -> list:
    """ Performs second search in order to optimize the features of the
    dataset and find the list of columns for which results are the best.
    Feature are dropped from dataset in a loop.
    Modelling is based on a basis of random search - random model parameters
    are choosen.
    Models with the best AUC metric and acceptable overfit are saved and stored
    Models are fitted in a while loop until maximum number of iterations or
    set elapse time is reached.
    After that results are exported to desired location.


    Parameters
    ----------
    train_data : pd.DataFrame
        tabular data with data to fit model on
    train_features : list
        list of features (independent variables) to be included in the model
        bar from label (output variable)
    test_data : pd.DataFrame
        tabular data with data to evaluate model performance on
    test_labels : list (of str values)
        array-like values of output variable
    columns_to_add : list
        list of features to add to the existing dataset (certain combination of
        features may give better results than complete list)
    max_iter : int
        stopping criterium in while loop - number of iterations for which
        different model classes will be generated
    max_hours : float
        stopping criterium in while loop (models will generated for that
        number of hours)
    target : str
        label - output variable
    min_auc : float
        minimum AUC with which model will be accepted
    max_overfit_auc : float
        maximum allowed overfit between train and test AUC
    prefix : str
        guid with which to export results (best models) to pointed location

    Returns
    -------
    models_list : list
        list of models that met the criteria of AUC and overfit (tensorflow
        objects)
    best_models_list : list
        list of model parametrs that met the criteria of AUC and overfit
    result_df : pd.DataFrame
        tabular results of all generated models with their parameters, metrics
    """
    # create output export directory if it doesn't exist
    os.getcwd()
    if not os.path.exists('model_training/results/nn'):
        os.makedirs('model_training/results/nn')
    export_path = r'model_training/results/nn/'

    # declare possible parameter values for narrow search
    lr = np.arange(0.005, 0.1, 0.005)
    batch_size = np.arange(20, 110, 10)
    units = [16, 32, 64, 128, 256]
    num_hidden_layers = [1, 2, 3, 4, 5, 6]
    epochs = [100, 150, 200]
    dropout = np.arange(0.1, 0.3, 0.05)
    optimizers = [Adam, SGD]  # Nadam, RMSprop,
    losses = ['binary_crossentropy']  # 'logcosh','mean_absolute_error' ,'poisson','mean_squared_error'
    activation = [relu, tanh, elu]  # ,exponential
    last_activations = [sigmoid]
    early_stop = EarlyStopping(monitor='val_loss',
                               min_delta=0.03,
                               patience=20,
                               verbose=0,
                               mode='min',
                               restore_best_weights=True)

    # adjust class weights to make sure 0 and 1 classes are treated equally as usually there is a scarcity of ones
    class_weights = dict(enumerate(
        class_weight.compute_class_weight('balanced',
                                          np.unique(test_labels),
                                          test_labels)))

    # create empty list to append with selected cols models
    temp_train_data = train_data
    temp_test_data = test_data
    best_models_list_params = []
    best_models_list_h5 = []
    # try models on trimmed dataset
    for idx, col in enumerate(columns_to_add):
        max_auc = 0
        used_columns = list(temp_train_data) + [col]
        best_models_local_params = []
        best_models_local_h5 = []
        models_list = []
        temp_train_data = temp_train_data[used_columns]
        temp_test_data = temp_test_data[used_columns]

        i = 0
        iteration_start_time = time.time()
        execution_time = 0
        while (execution_time < max_hours) and i != max_iter:
            curr_num_hidden_layers = num_hidden_layers[random.randrange(
                0, len(num_hidden_layers), 1)]
            last_activation = last_activations[random.randrange(
                0, len(last_activations), 1)]
            loss_function = losses[random.randrange(0, len(losses), 1)]
            optimizer_function = optimizers[random.randrange(
                0, len(optimizers), 1)]
            current_lr = lr[random.randrange(0, len(lr), 1)]
            current_epoch = epochs[random.randrange(0, len(epochs), 1)]
            current_batch_size = batch_size[random.randrange(
                0, len(batch_size), 1)]
            current_dropout = dropout[random.randrange(0, len(dropout), 1)]

            random.seed()
            model = Sequential()
            model.add(Dense(units[random.randrange(0, len(units), 1)],
                            input_dim=temp_train_data.shape[1],
                            activation=activation[random.randrange(0, len(activation), 1)]))

            for j in range(curr_num_hidden_layers):
                model.add(Dropout(current_dropout))
                model.add(Dense(units[random.randrange(0, len(units), 1)],
                                activation=activation[random.randrange(0, len(activation), 1)]))

            model.add(Dense(1,
                            activation=last_activation,
                            kernel_initializer='normal'))
            model.compile(loss=loss_function,
                          optimizer=optimizer_function(lr=current_lr),
                          metrics=['acc'])
            history = model.fit(temp_train_data,
                                train_features,
                                epochs=current_epoch,
                                batch_size=current_batch_size,
                                validation_split=0.2,
                                verbose=0,
                                callbacks=[early_stop],
                                class_weight=class_weights)
            test_predictions = model.predict(temp_test_data)
            predictions_df_test = pd.DataFrame(test_predictions)
            train_predictions = model.predict(temp_train_data)
            predictions_df_train = pd.DataFrame(train_predictions)

            auc_test = roc_auc_score(test_labels, predictions_df_test)
            auc_train = roc_auc_score(train_features, predictions_df_train)
            # for regression use val loss
            # auc = min(history.history['val_loss'])

            model_params = {'lr': current_lr,
                            'batch_size': current_batch_size,
                            'model_layers': model.get_config(),
                            'epochs': current_epoch,
                            'dropout': current_dropout,
                            'optimizer': str(optimizer_function),
                            'losses': loss_function,
                            'auc_train': auc_train,
                            'auc_test': auc_test,
                            'overfit': round((auc_train - auc_test), 3),
                            'columns_used': temp_test_data.columns.to_list()}

            if (auc_test > min_auc) and (auc_train - auc_test) < max_overfit_auc and (auc_train - auc_test) > -0.015:
                models_list.append(model)
                # append list with the best model on local search (current column selection)
                if auc_test > max_auc:
                    best_models_local_h5.append(model)
                    best_models_local_params.append(model_params)
                    max_auc = auc_test
            else:
                models_list.append(np.nan)
            K.clear_session()
            i = i + 1
            execution_time = (time.time() - iteration_start_time) / 3600
            print("Forward search. Iteration: {}. Time elapsed {}. \
                  Column added: {}. Layer: {}. AUC train: {}. AUC test: {}.".format(
                  str(i), execution_time, str(idx), str(j), str(auc_train), str(auc_test)))

        # append best models with the best model from current columns selection
        if best_models_local_h5:
            best_models_list_h5.append(best_models_local_h5[-1])
            best_models_list_params.append(best_models_local_params[-1])
            # export best model on current column selection
            best_models_local_h5[-1].save(export_path + str(prefix) +
                                          str(idx) + '.h5')

    # export parameters of best models of each columns selections
    best_models_results_df = pd.DataFrame(best_models_list_params)
    best_models_results_df.to_csv(export_path + str(prefix) + '_' +
                                  str(date.today()) + '.csv',
                                  index=False)
    return best_models_list_h5, best_models_list_params, best_models_results_df
