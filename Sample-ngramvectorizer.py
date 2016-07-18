import pickle
import os
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer
import re
from KNOW_2016_feature_generatorv9functions import populateFeatureAll
from KNOW_2016_feature_generatorv9functions import k_fold_generator
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

featureListTrain = []
featureListTest= []
if os.path.isfile('traindumpv3') and os.path.isfile('testdumpv3'):
    with open('traindumpv3','rb') as f:
        featureListTrain = pickle.load(f)
    with open('testdumpv3','rb') as f:
        featureListTest = pickle.load(f)
# Load of attribute and test values
with open('trainingDataset.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]

with open('testDatasetLabeled.tsv','r') as f:
    testsetAttributes=[x.strip().split('\t') for x in f][1:]

# Query caching prevents the algorithm to send DBpedia requests if it is already in the local storage
queryCache = set()
with open('querycache.txt','r') as f:
    lines = f.readlines()
    for line in lines:
        queryCache.add(line.replace("\n",""))
cacheFile = open('querycache.txt', 'a',encoding='utf-8')



ngram_vectorizer = CountVectorizer(analyzer='char_wb', ngram_range=(2, 2), min_df=1)
counts = ngram_vectorizer.fit_transform(['words', 'wprds'])

bigram_vectorizer = CountVectorizer(ngram_range=(1, 1),
                                    token_pattern=r'\b\w+\b', min_df=0, max_df=150)
from sklearn.feature_extraction.text import TfidfVectorizer
tfvectorizer = TfidfVectorizer(ngram_range=(1, 1),
                                    token_pattern=r'\b\w+\b', min_df=1)

vectorizer = bigram_vectorizer
#vectorizer.fit_transform(corpus)
X = ['Bi-grams are cool! But I am bad.', 'Bi-grams are bad! But I am cool.']
y = ['good','bad']
Xt = ['I are cool bad!', 'I am bad!']
y = ['good','bad']
tfvect = vectorizer.fit(X)
X_train_counts = tfvect.transform(X)
X_test_counts = tfvect.transform(Xt)

clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts, y)
predict = clf.predict(X_test_counts)
tfanalyzer = tfvect.build_analyzer()
# tripletext = ' <http://www.viziooptic.com/designer-eyeglasses/Lafont-I-Love-c.729-Eyeglasses-20005.aspx#product> <http://www.w3.org/2000/01/rdf-schema#comment> '
# triple = re.sub('[^0-9a-zA-Z ]+',"",tripletext)
#
# print(tfanalyzer(triple))
import nltk
from nltk.corpus import stopwords
stemmer = nltk.stem.snowball.EnglishStemmer(ignore_stopwords=False)
stop = stopwords.words('english')
X = []
y = []
Xt = []
yt =[]
for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                   # X.append(revs)
                   # y.append(row[6])
                    row.append(revs)
                    for feat in featureListTrain:
                        if feat['ID']== ID:
                            for f in feat:
                                row.append(re.sub('[^0-9a-zA-Z ]+',"",f)+str(feat[f]))
                   # print(tfanalyzer(revs))
            else:
                print("dosya yok")
                with open('MetacriticReviews/'+ID+'.txt', 'wb') as f:
                    f.write("")
        except BaseException as b:
            print(b)

for row in testsetAttributes:
    try:
        import os.path
        ID = row[0]
        if os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):
            with open('MetacriticReviewsTest/'+ID+'.txt', 'rb') as f:
                revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
               # Xt.append(revs)
                #yt.append(row[6])
                row.append(revs)
                for feat in featureListTest:
                    if feat['ID']== ID:
                        for f in feat:
                            row.append(" "+re.sub('[^0-9a-zA-Z ]+',"",f)+str(feat[f]))

        else:
            print(ID+"dosya yok")

    except BaseException as b:
        print(b)

for row in trainingsetAttributes:
    y.append(row[6])
    feats = ""
    for v in row[7:8]:
        feats += " "+ v
    X.append(feats)
for row in testsetAttributes:
    yt.append(row[6])
    feats = ""
    for v in row[7:8]:
        feats += " "+ v
    Xt.append(feats)

# for row in trainingsetAttributes:
#         try:
#             import os.path
#             ID = row[0]
#             if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
#                 with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
#                     revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
#                    # X.append(revs)
#                     X.append("")
#                     y.append(row[6])
#                    # print(tfanalyzer(revs))
#             else:
#                 print("dosya yok")
#                 with open('MetacriticReviews/'+ID+'.txt', 'wb') as f:
#                     f.write("")
#         except BaseException as b:
#             print(b)
# i=0
# try:
#     for row in featureListTrain:
#             for r in row:
#                 X[i] += " "+re.sub('[^0-9a-zA-Z ]+',"",r)+str(row[r])
#             i=i+1
# except BaseException as b:
#     print (i)


# for row in testsetAttributes:
#     try:
#         import os.path
#         ID = row[0]
#         if os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):
#             with open('MetacriticReviewsTest/'+ID+'.txt', 'rb') as f:
#                 revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
#                # Xt.append(revs)
#                 Xt.append("")
#                 yt.append(row[6])
#         else:
#             print(ID+"dosya yok")
#
#     except BaseException as b:
#         print(b)
#
# i=0
# for row in featureListTest:
#         for r in row:
#             Xt[i] += " "+re.sub('[^0-9a-zA-Z ]+',"",r)+str(row[r])
#         i=i+1

tfvect = vectorizer.fit(X)
X_train_counts = tfvect.transform(X)
X_test_counts = tfvect.transform(Xt)



names = ["Linear SVM","Nearest Neighbors",  "RBF SVM", "Decision Tree",
 "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
 "Quadratic Discriminant Analysis"]
# names = ["Linear SVM","Linear SVM","Linear SVM","Linear SVM"]

classifiers = [
SVC(kernel="linear", C=0.025),
KNeighborsClassifier(3),
SVC(gamma=2, C=1),
DecisionTreeClassifier(max_depth=5),
RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
AdaBoostClassifier(),
GaussianNB(),
LinearDiscriminantAnalysis(),
QuadraticDiscriminantAnalysis()]
# classifiers = [
# SVC(kernel="linear", C=0.025),
# SVC(kernel="linear", C=0.02),
# SVC(kernel="linear", C=0.01)
# ]

for name, clf in zip(names, classifiers):
    try:
        clf.fit(X_train_counts, y)
        score = clf.score(X_test_counts, yt)
        print(name+":"+str(score))
        #print (clf.predict(X_test_counts))
        #for xx in X_test:
            #print (xx['ID'])
        #for featDict in featureListTest:
        #    print(featDict['ID']+"\t"+clf.predict(X_test_counts))
    except BaseException as b:
        print (b)

        clf.fit(X_train_counts.toarray(), y)
        score = clf.score(X_test_counts.toarray(), yt)
        print(name+":"+str(score))

clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts, y)
score = clf.score(X_test_counts,yt)

print(tfanalyzer('Bi-grams are cool!'))
analyze = bigram_vectorizer.build_analyzer()
analyze('Bi-grams are cool!') == (
    ['bi', 'grams', 'are', 'cool', 'bi grams', 'grams are', 'are cool'])

ngram_vectorizer.get_feature_names() == (
    [' w', 'ds', 'or', 'pr', 'rd', 's ', 'wo', 'wp'])