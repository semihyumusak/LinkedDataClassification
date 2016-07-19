
import time

import re
from SPARQLWrapper import SPARQLWrapper, JSON,RDF, POST, GET, SELECT, CONSTRUCT, ASK, DESCRIBE
def populateFeatureAll (featDict, endpoint):
    URI = featDict['uri']
    getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)

def getAttributeWithoutCaching( sparqlquery, featDict,endpoint):
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(sparqlqueryConstruct)
        sparql.setReturnFormat(RDF)
        results = sparql.query().convert()
        try:
            for s,p,o in results:
                #print(result)
                #print ("%s %s %s"%s,p,o)
                featDict.update({p:o})
                #print (s +"\t"+p+"\t"+o)
            #for result in results["results"]["bindings"]:
            #    featDict.update({result["p"]["value"]:result["o"]["value"]})
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

