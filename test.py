import os.path
import pickle
import re

from SPARQLWrapper import SPARQLWrapper, JSON
from feature_generator_functions import populateFeatureAll
from feature_generator_functions import k_fold_generator
from feature_generator_functions import getAttributeWithoutCaching


# Load of attribute and test values
with open('trainingDatasetSample.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
with open('testDataset.tsv','r') as f:
    testsetAttributes=[x.strip().split('\t') for x in f][1:]

# # Query caching prevents the algorithm to send DBpedia requests if it is already in the local storage
# queryCache = set()
# with open('querycache.txt','r') as f:
#     lines = f.readlines()
#     for line in lines:
#         queryCache.add(line.replace("\n",""))
# cacheFile = open('querycache.txt', 'a',encoding='utf-8')

i = 0
featureListTest = []
featureListTrain = []

# Initialize Feature Sets
for row in trainingsetAttributes:
    URI = row[1].replace('"','')
    featureDictTrain = {"uri":URI}
    ID = row[0].replace('"','')
    featureDictTrain.update({"ID":ID})
    populateFeatureAll(featureDictTrain,"http://localhost:8891/sparql")
    print (i)
    i = i+1
    featureListTrain.append(featureDictTrain)


with open('trainingDatasetSample.tsv','r') as f:
    trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]

X=featureListTrain
y= trainingsetLabels

from sklearn.svm import SVC
from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()


fit = vec.fit(X)

print (fit.fit.get_feature_names())
