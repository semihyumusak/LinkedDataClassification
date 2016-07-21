import hashlib
import time
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
import re
from SPARQLWrapper import SPARQLWrapper, JSON,RDF, POST, GET, SELECT, CONSTRUCT, ASK, DESCRIBE
def populateFeatureAll (featDict, endpoint):
    URI = featDict['uri']
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p1 ?o1. ?o1 ?p ?o}",featDict,endpoint)

def getAttributeWithoutCaching( sparqlquery, featDict,endpoint):
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(sparqlqueryConstruct)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        try:
            #for s,p,o in results:
                #print(result)
                #print ("%s %s %s"%s,p,o)
#                featDict.update({p:o})
                #print (s +"\t"+p+"\t"+o)
            for result in results["results"]["bindings"]:
                if result["o"]["value"] is int or type(result["o"]["value"]) is float :
                    if abs(result["o"]["value"])<100000:
                        featDict.update({result["p"]["value"]:abs(result["o"]["value"])})
                    else:
                        print (result["p"]["value"] +" neglected")
                else :
                    if is_number(result["o"]["value"]):
                        if not result["p"]["value"].endswith("ID") and abs(int(float(result["o"]["value"])))<100000:
                            featDict.update({result["p"]["value"]:abs(int(float(result["o"]["value"])))})
                        else:
                            print (result["p"]["value"] +" neglected")
                    else:
                        featDict.update({result["p"]["value"]:hashlib.md5(result["o"]["value"].encode("UTF8")).hexdigest()})
        except BaseException as b:
            print (b)
    except BaseException as b:
        print (b)
        time.sleep(1)


def getNumericAttributeLocalValue  (sparqlquery, featDict, high, low, name ):

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlquery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    onerror=1
    while onerror:
        try:
            for result in results["results"]["bindings"]:
                try:
                    featDict.update({name:int(float(result["o"]["value"].split('/')[4]))})
                except BaseException as b:
                    print (b)
            onerror=0
        except BaseException as b:
            print (b)
            time.sleep(1)


def getNumericAttributeWithCaching( sparqlquery, featDict, high, low, name, URI ,queryCache, cacheFile):

    predicateName = URI+name
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    sparqlqueryAsk = "ASK {<%s> <%s> ?o.}"%(URI,predicateName)

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlqueryAsk)
    sparql.setReturnFormat(JSON)
    resultAsk = sparql.query().convert()

    numericSparqlQuery = "SELECT ?o WHERE { <%s> <%s> ?o}"%(URI,URI+name)
    if resultAsk["boolean"] or sparqlquery in queryCache:
        getNumericAttributeLocal( numericSparqlQuery, featDict, high, low, name )
    else:
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery(sparqlquery)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except BaseException as b:
            print (b)
            time.sleep(1)

        for result in results["results"]["bindings"]:
            sparql = SPARQLWrapper("http://localhost:3030/know2/update")
            updateQuery = "INSERT DATA {<%s> <%s> <%s>.}" % (URI,URI+name,str(result["o"]["value"]))
            sparql.setQuery(updateQuery)
            sparql.query()

    getNumericAttributeLocal( numericSparqlQuery, featDict, high, low, name )
    if sparqlquery not in queryCache:
        queryCache.add(sparqlquery)
        cacheFile.write(sparqlquery+"\n")

def k_fold_generator(X, y, k_fold):
    subset_size = int(len(X) / k_fold)
    for k in range(k_fold):
        X_train = X[:k * subset_size] + X[(k + 1) * subset_size:]
        X_valid = X[k * subset_size:][:subset_size]
        y_train = y[:k * subset_size] + y[(k + 1) * subset_size:]
        y_valid = y[k * subset_size:][:subset_size]

        yield X_train, y_train, X_valid, y_valid

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import SelectKBest, SelectPercentile,chi2
def PredictionScore (X_train,X_test,y_train,y_test,header):

    from sklearn.svm import SVC
    from sklearn.feature_extraction import DictVectorizer
    vec = DictVectorizer()


    names = ["Linear SVM","Nearest Neighbors",  "RBF SVM", "Decision Tree",
     "Random Forest", "AdaBoost", "Naive Bayes"]
    # names = ["Linear SVM","Linear SVM","Linear SVM","Linear SVM"]

    classifiers = [
    SVC(kernel="linear", C=0.025),
    KNeighborsClassifier(3),
    SVC(gamma=2, C=1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB()]
    # classifiers = [
    # SVC(kernel="linear", C=0.025),
    # SVC(kernel="linear", C=0.02),
    # SVC(kernel="linear", C=0.01)
    # ]

    for name, clf in zip(names, classifiers):
        try:
            accuracy = 0.0


            vec = DictVectorizer()
            fit = vec.fit(X_train)
            select = SelectPercentile(score_func=chi2,percentile=1).fit(fit.transform(X_train),y_train)
            fit.restrict (select.get_support())
            X_train_counts = fit.transform(X_train)
            X_test_counts = fit.transform(X_test)
            # clf = SVC(kernel="linear", C=0.025)
            try:
                clf.fit(X_train_counts.toarray(), y_train)
                #predict = clf.predict(X_test_counts.toarray())
                accuracy += clf.score(X_test_counts.toarray(),y_test)
                # coef = clf._get_coef()
               # print(np.argsort(coef)[-20:])
                #for i in range(0,len(X_test)):
                    #print (X_test[i]['ID']+"\t"+y_test[i]+"\t"+predict[i])
            except BaseException as b:
                    print (b)
            print (name+"\t"+header+"\t"+str(accuracy))
        except BaseException as b:
            print (b)
