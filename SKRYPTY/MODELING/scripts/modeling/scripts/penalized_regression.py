import numpy as np
import pandas as pd
import pickle

from datetime import timedelta, datetime
from random import randrange
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from time import time


# load normalized train and test data
train_data = pd.read_csv(r'model_training\data\PC\dataset_dummy_grouped_time_train_cat1.csv')
test_data = pd.read_csv(r'model_training\data\PC\dataset_dummy_grouped_time_test_cat1.csv')
print(len(train_data), sum(train_data['Label']), round(sum(train_data['Label']) / len(train_data) * 100, 4))
print(len(test_data), sum(test_data['Label']), round(sum(test_data['Label']) / len(test_data) * 100, 4))

# load features confirmed by boruta
boruta_importance = pd.read_excel('model_training/data/ai_assistant_dumps/PC/1_Documentation standard/Boruta_variable_importance_pc.xlsx')
boruta_importance = boruta_importance.sort_values(by=['normHits', 'meanImp'],
                                                  ascending=True)
boruta_features = list(
    boruta_importance[boruta_importance['decision'] == 'Confirmed'].V7)
boruta_pred_power = list(boruta_importance.V7)

# remove technical and label columns
train_id = train_data.pop('Unique')
test_id = test_data.pop('Unique')

train_labels = train_data.pop('Label')
test_labels = test_data.pop('Label')

train_datestamp = train_data.pop('datestamp')
test_datestamp = test_data.pop('datestamp')

### LOGISTIC REGRESSION - best model search
X_train = train_data[boruta_features]
X_test = test_data[boruta_features]

# 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99
# 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.1
print("Computing regularization path ...")
results = []
C = [i/2 + 0.5 for i in range(0, 20)]
for pos_weight, neg_weight in zip([0.33],
                                  [0.67]):
    for c in C:
        clf = linear_model.LogisticRegression(
            penalty='l1', C=c, solver='liblinear', tol=1e-6, max_iter=int(1e6),
            intercept_scaling=10000., class_weight={0: neg_weight,
                                                    1: pos_weight})

        clf.fit(X_train, train_labels)
        train_prob = clf.predict_proba(X_train)[:, 1]
        test_prob = clf.predict_proba(X_test)[:, 1]
        auc_train = roc_auc_score(train_labels, train_prob)
        auc_test = roc_auc_score(test_labels, test_prob)
        print('C:', c, 'auc_train', auc_train, 'auc_test', auc_test)
        if abs(auc_train - auc_test) < 0.1:
            results.append({'model': 'l1',
                            'penalty': c,
                            'auc_train': auc_train,
                            'auc_test': auc_test,
                            'overfit': round(auc_train - auc_test, 3),
                            'pos_weight': pos_weight,
                            'neg_weight': neg_weight,
                            'coefs': clf.coef_})

results_df = pd.DataFrame(results)

### run best model
coefs = {feature: coef for feature, coef in zip(
    boruta_features, list(results_df.iloc[0,]['coefs'][0])) if coef != 0}
features = list(coefs.keys())

best_model = linear_model.LogisticRegression(penalty='l1', solver='liblinear',
                                      C=0.485, tol=1e-6, max_iter=int(1e6),
                                      intercept_scaling=10000.,
                                      class_weight={0: 0.1,
                                                    1: 0.99})

best_model.fit(X_train[coefs.keys()], train_labels)

train_prob = best_model.predict_proba(X_train[coefs.keys()])[:,1]
test_prob = best_model.predict_proba(X_test[coefs.keys()])[:,1]

train_predictions_df = pd.DataFrame(train_prob)
test_predictions_df = pd.DataFrame(test_prob)

test_results = pd.concat([test_id, test_datestamp, test_predictions_df, test_labels], axis=1)
test_results = test_results.rename(columns={0: "Score"})
test_results = test_results.sort_values(by='Score', axis=0, ascending=False)

SumTest = pd.DataFrame(np.cumsum(test_results['Label']))
SumTest = SumTest.rename(columns={'Label': 'Sum'})
test_results = pd.concat([test_results, SumTest], axis=1)
test_results.reset_index(inplace=True, drop=True)
X_coordinates = pd.DataFrame(np.arange(1, (test_results.shape[0]+1)) / (test_results.shape[0]))
X_coordinates = X_coordinates.rename(columns={0: 'X_coordinates'})
y_coordinates = pd.DataFrame(test_results['Sum']/test_results['Sum'].max())
y_coordinates = y_coordinates.rename(columns={'Sum': 'y_coordinates'})
test_results = pd.concat([test_results, X_coordinates, y_coordinates], axis=1)

# train results
train_results = pd.concat([train_id, train_datestamp, train_predictions_df, train_labels], axis=1)
train_results = train_results.rename(columns={0: "Score"})
train_results = train_results.sort_values(by='Score', axis=0, ascending=False)

SumTrain = pd.DataFrame(np.cumsum(train_results['Label']))
SumTrain = SumTrain.rename(columns={'Label': 'Sum'})
train_results = pd.concat([train_results, SumTrain], axis=1)

train_results.reset_index(inplace=True, drop=True)
X_coordinates = pd.DataFrame(np.arange(1, (train_results.shape[0]+1))/(train_results.shape[0]))
X_coordinates = X_coordinates.rename(columns={0: 'X_coordinates'})
y_coordinates = pd.DataFrame(train_results['Sum']/train_results['Sum'].max())
y_coordinates = y_coordinates.rename(columns={'Sum': 'y_coordinates'})
train_results = pd.concat([train_results, X_coordinates, y_coordinates], axis=1)

auc_test = roc_auc_score(test_labels, test_predictions_df)
auc_train = roc_auc_score(train_labels, train_predictions_df)
print(auc_train, auc_test)

results_df.to_excel(r'model_training\results\PC\lr\5_Client Outreach\penalized_LR_results.xlsx')
test_results.to_csv(r'model_training\results\PC\lr\5_Client Outreach\lr_test_results.csv')
train_results.to_csv(r'model_training\results\PC\lr\5_Client Outreach\lr_train_results.csv')
pickle.dump(best_model, open(r'model_training\results\PC\lr\5_Client Outreach\penalized_LR_results.sav', 'wb'))
