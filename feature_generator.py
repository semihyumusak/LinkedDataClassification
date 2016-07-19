import os.path
import pickle
import re
from sklearn.feature_selection import VarianceThreshold
from SPARQLWrapper import SPARQLWrapper, JSON
from feature_generator_functions import populateFeatureAll
from feature_generator_functions import k_fold_generator
from feature_generator_functions import getAttributeWithoutCaching


# Load of attribute and test values
with open('trainingDatasetSample.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
with open('testDatasetLabeled.tsv','r') as f:
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
endpoint = "http://dbpedia.org/sparql"
#endpoint = "http://localhost:8891/sparql"
# Initialize Feature Sets
for row in trainingsetAttributes:
    URI = row[1].replace('"','')
    featureDictTrain = {"uri":URI}
    ID = row[0].replace('"','')
    featureDictTrain.update({"ID":ID})
    featureListTrain.append(featureDictTrain)

for row in testsetAttributes:
    URI = row[1].replace('"','')
    featureDictTest = {"uri":URI}
    ID = row[0].replace('"','')
    featureDictTest.update({"ID":ID})
    featureListTest.append(featureDictTest)

if os.path.isfile('traindumpv3') and os.path.isfile('testdumpv3'):
    with open('traindumpv3','rb') as f:
        featureListTrain = pickle.load(f)
    with open('testdumpv3','rb') as f:
        featureListTest = pickle.load(f)
else:
    # Populate Features
    for featDict in featureListTrain:
        i= i+1
        print(i)
        populateFeatureAll(featDict,endpoint)
    for featDict in featureListTest:
        i= i+1
        print(i)
        populateFeatureAll(featDict,endpoint)

    with open('traindumpv3','wb') as f:
        pickle.dump(featureListTrain, f)
    with open('testdumpv3','wb') as f:
        pickle.dump(featureListTest, f)

with open('trainingDatasetSample.tsv','r') as f:
    trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]
with open('testDatasetLabeled.tsv','r') as f:
    testsetLabels=[x.strip().split('\t')[6] for x in f][1:]

X=featureListTrain
y= trainingsetLabels

from sklearn.svm import SVC
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_selection import VarianceThreshold
import numpy
import hashlib
vec = DictVectorizer()
fit = vec.fit(X)

#support = SelectKBest(chi2,k=10).fit(fit.transform(X),y)
selector = VarianceThreshold(threshold=1)

#fit = fit.restrict(support.get_support())
selector = selector.fit(fit.transform(X))


X_train_counts = selector.transform(fit.transform(X))# fit.transform(X)
X_test_counts = selector.transform(fit.transform(featureListTest)) # fit.transform(featureListTest)
clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts.toarray(), y)
#predict = clf.predict(X_test_counts.toarray())

print("score " + str(clf.score(X_test_counts.toarray(),testsetLabels)))
exit()
#for v in predict:
#    print(v)

try:
        accuracy = 0.0
        for X_train, y_train, X_test, y_test in k_fold_generator(X, y, 10):

            vec = DictVectorizer()
            fit = vec.fit(X_train)

            X_train_counts = fit.transform(X_train)
            X_test_counts = fit.transform(X_test)
            clf = SVC(kernel="linear", C=0.025)
            try:
                clf.fit(X_train_counts.toarray(), y_train)
                predict = clf.predict(X_test_counts.toarray())
                accuracy += clf.score(X_test_counts.toarray(),y_test)
                for i in range(0,len(X_test)):
                    print (X_test[i]['ID']+"\t"+y_test[i]+"\t"+predict[i])
            except BaseException as b:
                    print (b)
        print (str(accuracy))
except BaseException as b:
    print (b)


import nltk
from nltk.corpus import stopwords
stemmer = nltk.stem.snowball.EnglishStemmer(ignore_stopwords=False)
stop = stopwords.words('english')

# ------ ADDING TEXT FEATURES

if os.path.isfile('traindumpv3text') and os.path.isfile('testdumpv3text'):
    with open('traindumpv3text','rb') as f:
        featureListTrain = pickle.load(f)
    with open('testdumpv3text','rb') as f:
        featureListTest = pickle.load(f)

else:
    import nltk

    def get_words_in_reviews(reviews):
        all_words = []
        for (words, sentiment) in reviews:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    # ------ ADDING TEXT FEATURES
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
    import re
    uncleanedreviews = []
    reviews = []
    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                    uncleanedreviews.append((revs,str(row[6])))
        except BaseException as b:
            print(b)

    for (words,sentiment) in uncleanedreviews:
        words_filtered = [stemmer.stem(e.lower()) for e in words.split() if len(e) >= 3 and stemmer.stem(e.lower()) not in stop]
        reviews.append((words_filtered, sentiment))
    word_features = get_word_features(get_words_in_reviews(reviews))

    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))

                    for featDict in featureListTrain:
                        if featDict['ID']==row[0].replace('"',''):
                            for word in revs.split():
                                root = stemmer.stem(word)
                                if root in word_features and root not in stop:
                                    featDict.update({root: 1})
            else:
                print("dosya yok")
        except BaseException as b:
            print(b)

    for row in testsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):
                with open('MetacriticReviewsTest/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                    for featDict in featureListTest:
                        if featDict['ID']==row[0].replace('"',''):
                            for word in revs.split():
                                root = stemmer.stem(word)
                                if root in word_features and root not in stop:
                                    featDict.update({root: 1})
            else:
                print(ID+"dosya yok")
        except BaseException as b:
            print(b)

    import re

    with open('traindumpv3text','wb') as f:
        pickle.dump(featureListTrain, f)
    with open('testdumpv3text','wb') as f:
        pickle.dump(featureListTest, f)

# ----- ENG TEXT FEATURES
with open('trainingDataset.tsv','r') as f:
    trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]

X=featureListTrain
y= trainingsetLabels

from sklearn.svm import SVC
from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()


fit = vec.fit(X)
X_train_counts = fit.transform(X)
X_test_counts = fit.transform(featureListTest)
clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts.toarray(), y)
predict = clf.predict(X_test_counts.toarray())

for v in predict:
    print(v)

try:
        accuracy = 0.0
        for X_train, y_train, X_test, y_test in k_fold_generator(X, y, 10):

            vec = DictVectorizer()
            fit = vec.fit(X_train)

            X_train_counts = fit.transform(X_train)
            X_test_counts = fit.transform(X_test)
            clf = SVC(kernel="linear", C=0.025)
            try:
                clf.fit(X_train_counts.toarray(), y_train)
                predict = clf.predict(X_test_counts.toarray())
                accuracy += clf.score(X_test_counts.toarray(),y_test)
                for i in range(0,len(X_test)):
                    print (X_test[i]['ID']+"\t"+y_test[i]+"\t"+predict[i])
            except BaseException as b:
                    print (b)
        print (str(accuracy))
except BaseException as b:
    print (b)


