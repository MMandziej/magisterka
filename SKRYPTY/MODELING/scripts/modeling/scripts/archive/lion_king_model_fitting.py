import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
from tensorflow.keras.models import load_model

from random_search_lion_king import random_search

# Importing data
train_dataset = pd.read_csv(r'data/Workflow_new_SP_DR_shiny_FS_train_dataset.csv')
test_dataset = pd.read_csv(r'data/Workflow_new_SP_DR_shiny_FS_test_dataset.csv')
full_dataset = pd.concat([train_dataset, test_dataset], axis=0)

cols_to_drop = [
    'GRID_ID', 'Label', 'Signatory_NO_errors_last_5_days',
    'Signatory_NO_cases_last_5_days', 'Signatory_NO_errors_last_month',
    'Signatory_NO_cases_month']

train_data = train_dataset.drop(cols_to_drop, axis=1)
test_data = test_dataset.drop(cols_to_drop, axis=1)
train_labels = train_dataset.pop('Label')
test_labels = test_dataset.pop('Label')
# train_id = train_dataset.pop('GRID_ID')
# test_id = test_dataset.pop('GRID_ID')

# Get output
models_list, output_table = random_search(
    train_data, train_labels, test_data, test_labels,
    max_iter=1000, max_hours=3.5, min_auc=0.65, max_overfit_auc=0.05)

# Compare results with the best model so far
best_model = load_model(r'final_model_DR.h5')
train_predictions = best_model.predict(train_data)
test_predictions = best_model.predict(test_data)
# Check auc scores of best model without cross validation
auc_train = roc_auc_score(train_labels, train_predictions)
auc_test = roc_auc_score(test_labels, test_predictions)

# Best model cross validation on full dataset (union on train & test)
full_data = full_dataset.drop(cols_to_drop, axis=1)
full_labels = full_dataset.pop('Label')
# full_id = full_id.pop('GRID_ID')

seed = np.random.RandomState(0)
# Stratified KFold validation
str_kfold_auc_scores = []
str_kf = StratifiedKFold(n_splits=5, random_state=seed, shuffle=True)
for train_index, test_index in str_kf.split(full_data, full_labels):
    X_train, y_train = full_data.iloc[train_index], full_labels.iloc[train_index]
    X_test, y_test = full_data.iloc[test_index], full_labels.iloc[test_index]
    history = best_model.fit(X_train, y_train)
    predictions = best_model.predict(X_test)
    str_kfold_auc_scores.append(roc_auc_score(y_test, predictions))
str_kfold_auc_mean = np.mean(str_kfold_auc_scores)
str_kfold_auc_std = np.std(str_kfold_auc_scores)

# Ordinary KFold cross validation
kfold_auc_scores = []
cv = KFold(n_splits=5, random_state=seed, shuffle=True)
for train_index, test_index in cv.split(full_data):
    X_test, y_test = full_data.iloc[test_index], full_labels.iloc[test_index]
    history = best_model.fit(X_train, y_train)
    predictions = best_model.predict(X_test)
    kfold_auc_scores.append(roc_auc_score(y_test, predictions))
kfold_auc_mean = np.mean(kfold_auc_scores)
kfold_auc_std = np.std(kfold_auc_scores)
