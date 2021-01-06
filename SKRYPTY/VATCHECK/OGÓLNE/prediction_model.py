import pandas as pd
import pydotplus

from IPython.display import Image
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.externals.six import StringIO  
from sklearn.model_selection import train_test_split
from sklearn import metrics


from xgboost import XGBClassifier
#from sklearn.metrics import accuracy_score

data = pd.read_excel(r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\ML_EMIS_SAMPLE.xlsx")

cols = list(data.columns)
indnt_features = [
    'AddresFlat', 'AffilatteshipAvg', 'AffilatteshipMax', 'AffilatteshipMin', 'AffilatteshipsTotal', 'AffiliatesCount',
    'AffiliatesEMIS', 'AffiliatesForeign', 'AuditDateNull', 'AuditDateYearsAgo', 'OwnersCount', 'OwnersInEMIS',
    'PhoneNotPresent', 'PreviousNameChangeYearsAgo', 'PreviousNamesCount', 'IncorporationYear', 'DescriptionNull',
    'MainNAICSCount', 'MainProductsNull', 'MarketCapNull', 'EmployeesNumber', 'SecondaryPKDCount', 'SegmentPresence',
    'WebsiteNotPresent', 'DividendCount', 'DividendDate2YearsAgo', 'DividendPresent', 'EmailAdressNotPresent',
    'EmailAdressPublic', 'EmployeesNumberDate3YearsAgo', 'ExecutivesCount', 'ExternalIdsOthers', 'FaxNotPresent']

x = data[indnt_features]
y = data.Label

seed = 7
train_set = 0.7
test_set = round(1-train_set, 1)

x_train, x_test, y_train, y_test = train_test_split(x,
                                                    y,
                                                    train_size=train_set,
                                                    test_size=test_set,
                                                    random_state=seed,
                                                    shuffle=True)

# Model
# Create Decision Tree classifer object
clf = DecisionTreeClassifier()
clf = clf.fit(x_train, y_train)
y_pred = clf.predict(x_test)
pred_accuracy = metrics.accuracy_score(y_test, y_pred)

# entropy
clf_ent = DecisionTreeClassifier(criterion="entropy")
clf_ent = clf_ent.fit(x_train, y_train)
y_pred_ent = clf_ent.predict(x_test)
pred_accuracy_ent = metrics.accuracy_score(y_test, y_pred_3)

# xgboost
model = XGBClassifier()
model.fit(x_train, y_train)
print(model)
y_pred_xgboost = model.predict(x_test)
y_xgboost_predictions = [round(value) for value in y_pred_xgboost]
pred_accuracy_ent = metrics.accuracy_score(y_test, y_xgboost_predictions)



# Visualisation
dot_data = StringIO()
export_graphviz(clf,
                out_file=dot_data,  
                filled=True,
                rounded=True,
                special_characters=True,
                feature_names=indnt_features,
                class_names=['Correct','Fraud'])
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
graph.write_png(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\FraudDetection.png')
Image(graph.create_png())
