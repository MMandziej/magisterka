import imblearn
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datetime import timedelta, datetime
from imblearn.over_sampling import RandomOverSampler, SMOTE
from random import randrange
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.svm import l1_min_c
from time import time


# load normalized train and test data
train_data = pd.read_csv(r'model_training\data\PC\dataset_dummy_grouped_time_train_cat7.csv')
test_data = pd.read_csv(r'model_training\data\PC\dataset_dummy_grouped_time_test_cat7.csv')
full_data = pd.concat([train_data, test_data], axis=0)
boruta = pd.read_excel(r'model_training\data\ai_assistant_dumps\PC\7_ODD (Office Due Diligence) - local requirements (if applicable)/Boruta_variable_importance_pc.xlsx')
boruta_features = list(boruta[boruta.decision == 'Confirmed']['V7'])

# get count of each class
full_data.Label.value_counts()
full_data.Label.value_counts().plot(kind='bar', title='Count (Label)')
count_class_0, count_class_1 = full_data.Label.value_counts()

# divide by class
df_class_0 = full_data[full_data['Label'] == 0]
df_class_1 = full_data[full_data['Label'] == 1]

# random oversampling
df_class_1_over = df_class_1.sample(count_class_0, replace=True)
df_test_over = pd.concat([df_class_0, df_class_1_over], axis=0)

X = full_data.iloc[:, :-1]
y = full_data['Label']


smote = SMOTE(sampling_strategy=0.055,
              random_state=123)
X_sm, y_sm = smote.fit_sample(X, y)

def random_date(row):
    datestamp = row.datestamp
    start = datetime.strptime('1/2/2020 8:00 AM', '%m/%d/%Y %I:%M %p').date()
    end = datetime.strptime('6/7/2020 6:00 PM', '%m/%d/%Y %I:%M %p').date()
    delta = end - start
    if pd.isna(datestamp):
        datestamp = start + timedelta(days=randrange(delta.days))
    return str(datestamp)

full_data_sm = X_sm.merge(full_data[['Unique', 'datestamp']], how='left', on='Unique')
full_data_sm['datestamp'] = full_data_sm.apply(random_date, axis=1)
df_sm_class_0 = full_data_sm[full_data_sm['Label'] == 0]
df_sm_class_1 = full_data_sm[full_data_sm['Label'] == 1]
#full_data_sm.to_csv(r'model_training\data\PC\8_FATCA_CRS\full_data_smote_cat7.csv')


### LOGISTIC REGRESSION
X_train = train_data.iloc[:, :-1][boruta_features]
X_test = test_data.iloc[:, :-1][boruta_features]
y_train = train_data['Label']
y_test = test_data['Label']


print("Computing regularization path ...")
start = time()


#cs = l1_min_c(X, y, loss='log') * np.logspace(0, 7, 8)
clf = linear_model.LogisticRegression(penalty='l1', solver='liblinear',
                                      tol=1e-6, max_iter=int(1e6),
                                      intercept_scaling=10000.)

results = []
C = [50, 25, 20, 15, 10, 9, 8, 7, 6, 5, 2, 1, 0.9]#, 0.8, 0.7, 0.6, 0.5]#, 0.4, 0.3, 0.2, 0.1, 0.05, 0.001]
for pos_weight, neg_weight in zip([0.9, 0.91, 0.92, 0.93], [0.1, 0.09, 0.08, 0.07]):
    for c in C:
        clf.set_params(C=c)
        clf.set_params(class_weight={1: pos_weight,
                                     0: neg_weight})
        clf.fit(X_train, y_train)
        train_prob = clf.predict_proba(X_train)[:,1]
        test_prob = clf.predict_proba(X_test)[:,1]
        auc_train = roc_auc_score(y_train, train_prob)
        auc_test = roc_auc_score(y_test, test_prob)
        print('C:', c, 'auc_train', auc_train, 'auc_test', auc_test)
        #print('Training accuracy:', clf.score(X_train, y_train))
        #print('Test accuracy:', clf.score(X_test, y_test))
        results.append({'penalty': c,
                        'auc_train': auc_train,
                        'auc_test': auc_test,
                        'overfit': round(auc_train - auc_test, 3),
                        'pos_weight': pos_weight,
                        'neg_weight': neg_weight})

results_df = pd.DataFrame(results)
