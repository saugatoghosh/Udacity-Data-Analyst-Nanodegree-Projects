# %load poi_id.py
#!/usr/bin/python

import sys
import pickle
sys.path.append("C:/Users/Saugata/gitrepos/ud120-projects/tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','to_messages', 'from_poi_to_this_person', 'from_messages', 
'from_this_person_to_poi', 'shared_receipt_with_poi', 'salary', 
'deferral_payments', 'total_payments', 'loan_advances', 
'bonus', 'restricted_stock_deferred', 'deferred_income', 
'total_stock_value', 'expenses', 'exercised_stock_options', 
'other', 'long_term_incentive', 'restricted_stock', 'director_fees'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Explore the data
## Total number of data points
print len(data_dict)

## Allocation across classes(POI/non-POI)
count = 0
for key in data_dict:
    if data_dict[key]['poi'] == 1:
        count+=1
print count

## Number of features with missing values

missing_list = []  
for key in data_dict:
    for k in data_dict[key]:
        if data_dict[key][k] == 'NaN':
            missing_list.append(k)

missing_set = set(missing_list)
print 'features with missing values' , missing_set

### Impute missing email features to mean
email_features = ['to_messages',
                  'from_poi_to_this_person',
                  'from_messages',
                  'from_this_person_to_poi',
                  'shared_receipt_with_poi']
from collections import defaultdict
email_feature_sums = defaultdict(lambda:0)
email_feature_counts = defaultdict(lambda:0)

for key in data_dict:
    for ef in email_features:
        if data_dict[key][ef] != "NaN":
            email_feature_sums[ef] += data_dict[key][ef]
            email_feature_counts[ef] += 1

email_feature_means = {}
for ef in email_features:
    email_feature_means[ef] = float(email_feature_sums[ef]) / float(email_feature_counts[ef])

for key in data_dict:
    for ef in email_features:
        if data_dict[key][ef] == "NaN":
            data_dict[key][ef] = email_feature_means[ef]


### Task 2: Remove outliers
data_dict.pop('TOTAL')
data_dict.pop('LOCKHART EUGENE E')
data_dict.pop('THE TRAVEL AGENCY IN THE PARK')


### Task 3: Create new feature(s)
def computeFraction( numerator, denominator):
    """ given a number messages to/from POI (numerator) 
        and number of all messages to/from a person (denominator),
        return the fraction of messages to/from that person
        that are from/to a POI
   """
    fraction = 0.
    if numerator == "NaN" or denominator == "NaN":
        return 0
    else:
        fraction = numerator/float(denominator)

    return fraction

for name in data_dict:

    data_point = data_dict[name]


    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = computeFraction( from_poi_to_this_person, to_messages )
 
    data_point["fraction_from_poi"] = fraction_from_poi
    
    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = computeFraction( from_this_person_to_poi, from_messages )

    data_point["fraction_to_poi"] = fraction_to_poi
    
    
features_list.append('fraction_from_poi')
features_list.append('fraction_to_poi')

print len(data_dict['SKILLING JEFFREY K'])

### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn import preprocessing
from sklearn import feature_selection
from sklearn.feature_selection import chi2, f_classif, SelectKBest
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV

#Build estimators for pipeline
#f_minmaxscaler = preprocessing.MinMaxScaler()
#dim_reduc = PCA()
kbest = SelectKBest()
dt_clf = DecisionTreeClassifier(random_state = 42)

estimator = [('kbest', kbest), ('dt_clf', dt_clf)]
pipe = Pipeline(estimator)


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!

param_grid = {
    'kbest__k' : [2,3,4,5,10,15,20],
    'dt_clf__criterion' : ['gini', 'entropy'],
    'dt_clf__min_samples_split' : [2,4,10,20],
    }
cv = StratifiedShuffleSplit(labels, 10, random_state=42)
clf= GridSearchCV(pipe, param_grid = param_grid,scoring = 'f1',cv = cv)
clf.fit(features, labels)
clf.best_params_ #the parameter combination that together got the best f1 score
clf = clf.best_estimator_ #a fitted pipeline with those best parameters

from tester import test_classifier
print ' '
# use test_classifier to evaluate the model
# selected by GridSearchCV
print "Tester Classification report:" 
test_classifier(clf, my_dataset, features_list)
print ' '


### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)

# Print features selected and their importances
features_selected=[features_list[i+1] for i in clf.named_steps['kbest'].get_support(indices=True)]
scores = clf.named_steps['kbest'].scores_
importances = clf.named_steps['dt_clf'].feature_importances_
import numpy as np
indices = np.argsort(importances)[::-1]
print 'The ', len(features_selected), " features selected and their importances:"
for i in range(len(features_selected)):
    print "feature no. {}: {} ({}) ({})".format(i+1,features_selected[indices[i]],importances[indices[i]], scores[indices[i]])

