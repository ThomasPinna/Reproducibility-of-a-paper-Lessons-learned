import sklearn
from sklearn import datasets
from sklearn.cross_validation import cross_val_score, cross_val_predict
from sklearn.feature_extraction import DictVectorizer
from sklearn import linear_model
import numpy as np
from scipy import stats
import json
from sklearn.svm import SVR
from sklearn.feature_selection import chi2
import sys


if __name__ == "__main__":
	#read data
	data = []
	with open(sys.argv[1]) as filey:
		data = json.load(filey)
	#transform to features
	features = []
	targets = []
	for dat in data:
		targets.append(dat["bugfix_time"])
		feat_set = []
		#feat_set.append(dat["developer_reputation"])
		feat_set.append(dat["dependencies"])
		feat_set.append(dat["attachments"])
		feat_set.append(dat["bug_severity"])
		feat_set.append(dat["nr_of_developers"])
		features.append(feat_set)

	lr = linear_model.LinearRegression()
	lr.fit(features,targets)

	print("==="+sys.argv[1]+"===")
	print("adjusted R2, R2 score of multivariate regression")
	r2 = lr.score(features, targets)
	adjr2 = 1 - float(len(targets)-1)/(len(targets)-len(features[0])-1)*(1-r2)
	print([adjr2, r2])

	predictions = list(cross_val_predict(lr, features, targets, cv=10))
	for x in range(len(predictions)):
		predictions[x] = [predictions[x]]
	print("F-value and p-value of multivariate regression")
	f = list(sklearn.feature_selection.f_regression(predictions, targets, center=True))
	print(f)
	print("F-value and p-value of univariate regression for (dependencies, attachments, bug_severity,nr_of_developers)")
	f_Regr = sklearn.feature_selection.f_regression(features, targets, center=True)
	print(list(f_Regr[0]))
	print(list(f_Regr[1]))
	

