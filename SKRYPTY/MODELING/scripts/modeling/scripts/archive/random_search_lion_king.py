"""
Created on Mon Mar 23 13:42:11 2020

Function used to iteratively test different models with randomly assigned
parameters values and choose the ones that met set criteria.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import os
import pandas as pd

from datetime import date
from keras import losses, optimizers
from random import randrange
from tensorflow import keras
from time import time

from keras.layers import Activation, Dense
from sklearn.metrics import roc_auc_score
from sklearn.utils import class_weight

from tensorflow.keras import backend as K, layers, losses, metrics, optimizers
from tensorflow.keras.activations import elu, exponential, hard_sigmoid, linear,\
    relu, sigmoid, softmax, relu, tanh
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dropout, Dense
from tensorflow.keras.optimizers import Adadelta, Adam, Nadam, RMSprop, SGD
from tensorflow.keras.losses import binary_crossentropy, categorical_crossentropy,\
    logcosh, mean_absolute_error, mean_squared_error, poisson


def random_search(train_data,
                  train_labels,
                  test_data,
                  test_labels,
                  max_iter=100,
                  max_hours=5,
                  target='Label',
                  min_auc=0.6,
                  max_overfit_auc=0.05):
    """ Performs search for promising model types (neural networks)
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
    train_labels : pd.Series
        array-like column with values of label (output) variable
    test_data : pd.DataFrame
        tabular data with data to evaluate model performance on
    test_labels : pd.Series
        array-like column with values of label (output) variable
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

    Returns
    -------
    models_list : list
        list of models that met the criteria of AUC (tensorflow objects)
    result_df : pd.DataFrame
        tabular results of all generated models with their parameters, metrics
    """

    # create output export directory if it doesn't exist
    os.getcwd()
    if not os.path.exists('random_search_results'):
        os.makedirs('random_search_results')
    export_path = r'random_search_results/'

    # set values for random search
    lr = np.arange(0.005, 0.1, 0.005)
    batch_size = np.arange(20, 110, 10)
    units = [16, 32, 64, 128, 256]
    num_hidden_layers = [1, 2, 3, 4, 5, 6]
    epochs = [100, 150, 200, 250, 300, 350]
    dropout = np.arange(0, 0.5, 0.1)
    optimizers = [Adam, SGD]  # Nadam, RMSprop
    losses = ['binary_crossentropy']  # 'logcosh', 'mean_absolute_error', 'poisson', 'mean_squared_error'
    activation = [relu, tanh, elu]  # exponential
    last_activations = [sigmoid]
    # early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=50)
    early_stop = EarlyStopping(monitor='val_loss',
                               min_delta=0.01,
                               patience=30,
                               verbose=0,
                               mode='min',
                               restore_best_weights=True)
    class_weights = dict(enumerate(
        class_weight.compute_class_weight('balanced',
                                          np.unique(test_labels),
                                          test_labels)))

    # build model based on parameters choosen by talos optimalization
    # initialize lists to append with model results
    models_list = []
    results = []
    start_time = time()
    execution_time = 0
    i = 0
    while (execution_time < max_hours) and i != max_iter:
        curr_num_hidden_layers = num_hidden_layers[randrange(0,
                                                             len(num_hidden_layers),
                                                             1)]
        last_activation = last_activations[randrange(0,
                                                     len(last_activations),
                                                     1)]
        loss_function = losses[randrange(0, len(losses), 1)]
        optimizer_function = optimizers[randrange(0, len(optimizers), 1)]
        current_lr = lr[randrange(0, len(lr), 1)]
        current_epoch = epochs[randrange(0, len(epochs), 1)]
        current_batch_size = batch_size[randrange(0, len(batch_size), 1)]
        current_dropout = dropout[randrange(0, len(dropout), 1)]

        model = Sequential()
        model.add(Dense(units[randrange(0, len(units), 1)],
                        input_dim=train_data.shape[1],
                        activation=activation[randrange(0, len(activation), 1)]))
        model.add(Dropout(current_dropout))
        for j in range(curr_num_hidden_layers):
            model.add(Dense(units[randrange(0, len(units), 1)],
                            activation=activation[randrange(0, len(activation), 1)]))
        model.add(Dense(1,
                        activation=last_activation,
                        kernel_initializer='normal'))
        model.compile(loss=loss_function,
                      optimizer=optimizer_function(lr=current_lr),
                      metrics=['acc'])

        try:
            model.fit(train_data,
                      train_labels,
                      epochs=current_epoch,
                      batch_size=current_batch_size,
                      validation_split=0.2,
                      verbose=0,
                      callbacks=[early_stop],
                      class_weight=class_weights)
        except Exception as e:
            error = 'Code: {}, Message: {}'.format(type(e).__name__, str(e))
            print(error)

        test_predictions = model.predict(test_data)
        predictions_df_test = pd.DataFrame(test_predictions)
        train_predictions = model.predict(train_data)
        predictions_df_train = pd.DataFrame(train_predictions)
        auc_train = roc_auc_score(train_labels, predictions_df_train)
        auc_test = roc_auc_score(test_labels, predictions_df_test)

        # for regression use val loss
        # auc = min(history.history['val_loss'])

        model_params = {'lr': current_lr,
                        'batch_size': current_batch_size,
                        'model_layers': model.get_config(),
                        'epochs': current_epoch,
                        'dropout': current_dropout,
                        'optimizer': str(optimizer_function),
                        'losses': loss_function,
                        'auc_test': auc_test,
                        'auc_train': auc_train,
                        'columns_used': test_data.columns.to_list()}
        # append results table with the latest model parameters and metrics
        results.append(model_params)

        if auc_test > min_auc and (auc_train - auc_test) < max_overfit_auc:
            models_list.append(model)
        else:
            models_list.append(np.nan)
        i = i + 1
        execution_time = (time() - start_time) / 3600
        print("Iteration: {}. Time elapsed: {}".format(str(i),
                                                       round(execution_time, 4)))
    results_df = pd.DataFrame(results)
    results_df.to_csv(export_path + 'results_modelling_' +
                      str(date.today()) + '.csv')
    return models_list, results_df
