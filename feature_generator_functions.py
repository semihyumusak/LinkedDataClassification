
import time

import re
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET, SELECT, CONSTRUCT, ASK, DESCRIBE
def populateFeatureAll (featDict):
    URI = featDict['uri']
    getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict)

def getAttributeWithoutCaching( sparqlquery, featDict):
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(sparqlqueryConstruct)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except BaseException as b:
        print (b)
        time.sleep(1)
    try:
        for result in results["results"]["bindings"]:
            featDict.update({result["p"]["value"]:result["o"]["value"]})
    except BaseException as b:
        print (b)
def getAttributeWithCaching( sparqlquery, featDict,queryCache, cacheFile):
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    sparqlqueryAsk = "ASK {"+sparqlqueryBase+"}"

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlqueryAsk)
    sparql.setReturnFormat(JSON)
    resultAsk = sparql.query().convert()

    if resultAsk["boolean"] or sparqlquery in queryCache:
        getAttributeLocal(sparqlquery, featDict, "http://localhost:3030/know2/query")
    else:
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery(sparqlqueryConstruct)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except BaseException as b:
            print (b)
            time.sleep(1)
        try:
            for result in results["results"]["bindings"]:
                sparql = SPARQLWrapper("http://localhost:3030/know2/update")
                if (str(result["o"]["value"])).startswith("http"):
                    updateQuery = "INSERT DATA {<%s> <%s> <%s>.}" % (str(result["s"]["value"]),str(result["p"]["value"]),str(result["o"]["value"]))
                else:
                    if str(result["o"]["value"]).isnumeric() :
                        updateQuery = "INSERT DATA {<%s> <%s> %s.}" % (str(result["s"]["value"]),str(result["p"]["value"]),str(result["o"]["value"]))
                    else:
                        updateQuery = "INSERT DATA {<%s> <%s> '%s'.}" % (str(result["s"]["value"]),str(result["p"]["value"]),re.sub('[^0-9a-zA-Z_-]+', '',result["o"]["value"]))
                sparql.setQuery(updateQuery)
                sparql.query()
        except BaseException as b:
            print (b)#+" "+"INSERT DATA "+ result["s"]["value"]+result["p"]["value"]+result["o"]["value"])
        getAttributeLocal(sparqlquery, featDict, "http://localhost:3030/know2/query")
    if sparqlquery not in queryCache:
        queryCache.add(sparqlquery)
        cacheFile.write(sparqlquery+"\n")



def getAttributeLocal (sparqlquery, featDict, localuri ):
    onerror = 1
    while onerror:
        try:
            sparql2 = SPARQLWrapper(localuri)
            sparql2.setQuery(sparqlquery)
            sparql2.setReturnFormat(JSON)
            results = sparql2.query().convert()

            for result in results["results"]["bindings"]:
                featDict.update({result["o"]["value"]:1})

            onerror = 0
        except BaseException as b:
            print (b)
            time.sleep(1)



def getNumericAttributeLocal  (sparqlquery, featDict, high, low, name ):

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlquery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    onerror=1
    while onerror:
        try:
            for result in results["results"]["bindings"]:
                try:
                    if int(float(result["o"]["value"].split("/")[4]))>= high:
                        featDict.update({name:"High"})
                    if int(float(result["o"]["value"].split("/")[4]))< high and int(float(result["o"]["value"].split("/")[4]))>low :
                        featDict.update({name:"Mid"})
                    if int(float(result["o"]["value"].split("/")[4]))<=low :
                        featDict.update({name:"Low"})
                except BaseException as b:
                    print (b)
            onerror=0
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

