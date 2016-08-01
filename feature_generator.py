
# def populateFeatureAll1 (featDict, endpoint):
#     from feature_generator_functions import getAttributeWithoutCaching
#     URI = featDict['uri']
#     #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
#     getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
#     #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p1 ?o1. ?o1 ?p ?o}",featDict,endpoint)
#
# def populateFeatureAll2 (featDict, endpoint):
#     from feature_generator_functions import getAttributeWithoutCaching
#     URI = featDict['uri']
#     #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
#     #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
#     getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p1 ?o1. ?o1 ?p ?o}",featDict,endpoint)


def CountPopulator (featDict,propertyList, queries, endpoint,previousDump):

        for sparqlquery in queries:
            import hashlib
            hashid = str(hashlib.md5(sparqlquery[0].encode("UTF8")).hexdigest())
            isCached = 0
            for dump in previousDump:
                if dump[0] == hashid:
                    isCached = 1
                    # for id,dic in dump[1].items():
                    #     propertyList.append(dic)
                        # if featDict["ID"] == rec["ID"]:
                    for r in dump[1]:
                        propertyList.append((r[0],r[1]))
            if not isCached:
                URI = featDict['uri']
                from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET, SELECT, CONSTRUCT, ASK, DESCRIBE
                try:
                    sparql = SPARQLWrapper(endpoint)#"http://dbpedia.org/sparql")
                    sparql.setQuery(sparqlquery[0].replace("URI",URI))
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    for result in results["results"]["bindings"]:
                        propertyList.append ((str(result["p"]["value"])+"_count"+str(sparqlquery[1]),int(result["o"]["value"])))
                except BaseException as b:
                    print (b)
def propertyStatistics (featureList,endpoint, queries,previousDump):

    propertyCountDict = {}
    allqueriesstr=""
    for query in queries:
        allqueriesstr += str(query[0])

    import hashlib
    import os
    import pickle

    id = str(hashlib.md5(allqueriesstr.encode("UTF8")).hexdigest())

    if os.path.isfile('dumps/statsDump_'+id):
        with open('dumps/statsDump_'+id,'rb') as f:
            propertyCountDict = pickle.load(f)
    else:

            from feature_generator_functions import propertyValues
            propertyList = []

            if os.path.isfile('dumps/propertyCountDump_'+id):
                with open('dumps/propertyCountDump_'+id,'rb') as f:
                    propertyList = pickle.load(f)
            else:
                # POPULATE COUNTS OF PROPERTIES
                for featDict in featureList:
                    CountPopulator(featDict,propertyList,queries, endpoint,previousDump)
                propertyList.sort()
                with open('dumps/propertyCountDump_'+id,'wb') as f:
                    pickle.dump(propertyList, f)
            # COUNT THE NUMBER OF PROPERTIES AND CALCULATE 80th percentile and 60th percentile

            prevName = ""
            count = 0
            localCount = 0
            #propertyCountDict = {}
            p = propertyValues()
            for tuple in propertyList:
                tupleName = tuple[0]
                tupleVal = tuple[1]
                if p.max < tupleVal:
                    p.max = tupleVal
                if p.min > tupleVal:
                    p.min = tupleVal
                p.total = p.total+tupleVal
                p.count = p.count +1
                if tupleName != prevName:
                    if prevName !="":
                        p.lowLimit = p.total/p.count + (p.total/p.count )/5 #60 rakami icin avg + avg/5
                        p.highLimit = p.max - (p.total/p.count/5)*2  #80 rakami icin max -avg*0.4
                        propertyCountDict.update({prevName:p})
                        p = propertyValues()
                    print (tupleName)
                    prevName = tupleName

                count = count+1

            propertyCountDict.update({prevName:p})
            with open('dumps/statsDump_'+id,'wb') as f:
                pickle.dump(propertyCountDict, f)

    return propertyCountDict



def populateFeatureAll (featDict, endpoint, queries,previousDump):
    from feature_generator_functions import getAttributeWithoutCaching
    URI = featDict['uri']
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    for query in queries:
        getAttributeWithoutCaching(query[0],URI,featDict,endpoint,previousDump)
def populateFeatureCounts (featDict, endpoint, queries,propertyStats,previousDump):
    from feature_generator_functions import getCountAttributeWithoutCaching
    URI = featDict['uri']
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    for query in queries:
        getCountAttributeWithoutCaching(query,URI, featDict,endpoint,propertyStats,previousDump)



def Main(endpoint, queries):
    import os.path
    import pickle
    import hashlib
    previousTestDumps = []
    previousTrainDumps = []
    previousStatsDumps = []
    for query in queries:
        id = str(hashlib.md5(query[0].encode("UTF8")).hexdigest())
        tempList=[]

        if os.path.isfile('dumps/testdump'+id):
            with open('dumps/testdump'+id,'rb') as f:
                tempList = pickle.load(f)
                previousTestDumps.append((id,tempList))
        if os.path.isfile('dumps/traindump'+id):
            with open('dumps/traindump'+id,'rb') as f:
                tempList = pickle.load(f)
                previousTrainDumps.append((id,tempList))
        if os.path.isfile('dumps/propertyCountDump_'+id):
            with open('dumps/propertyCountDump_'+id,'rb') as f:
                tempList = pickle.load(f)
                previousStatsDumps.append((id,tempList))


    numericQueries = []
    textQueries = []
    for query in queries:
        if "N" in query[1]:
            numericQueries.append(query)
        if "T" in query[1]:
            textQueries.append(query)

    import io
    outFile = open('output.txt', 'a')
    print ("---------------------------------------")
    outFile.write("---------------------------------------"+"\n")

    allqueriesstr= ""
    for query in queries:
        print(query[0])
        outFile.write(query[0]+"\n")
        allqueriesstr += str(query[0])

    outFile.close()

    import hashlib
    id = str(hashlib.md5(allqueriesstr.encode("UTF8")).hexdigest())
    import os.path
    import pickle

    # Load of attribute and test values
    with open('trainingDataset.tsv','r') as f:
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

    propertyStats = {}

    #endpoint = "http://dbpedia.org/sparql"
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


    propertyStats = propertyStatistics(featureListTrain,endpoint,numericQueries,previousStatsDumps)

    if os.path.isfile('dumps/testdump'+id):
        with open('dumps/testdump'+id,'rb') as f:
            featureListTest = pickle.load(f)
    else:
        for featDict in featureListTest:

            i= i+1
            print(i)
            populateFeatureAll(featDict,endpoint,textQueries,previousTestDumps)
            populateFeatureCounts(featDict,endpoint,numericQueries,propertyStats,previousTestDumps)

        with open('dumps/testdump'+id,'wb') as f:
            pickle.dump(featureListTest, f)


    if os.path.isfile('dumps/traindump'+id):
        with open('dumps/traindump'+id,'rb') as f:
            featureListTrain = pickle.load(f)
    else:
        # Populate Features
        for featDict in featureListTrain:
            i= i+1
            print(i)
            populateFeatureAll(featDict,endpoint,textQueries,previousTrainDumps)
            populateFeatureCounts(featDict,endpoint,numericQueries,propertyStats,previousTrainDumps)

        with open('dumps/traindump'+id,'wb') as f:
            pickle.dump(featureListTrain, f)

    with open('trainingDataset.tsv','r') as f:
        trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]
    with open('testDatasetLabeled.tsv','r') as f:
        testsetLabels=[x.strip().split('\t')[6] for x in f][1:]

    X=featureListTrain
    y= trainingsetLabels

    from feature_generator_functions import PredictionScore

    PredictionScore(X,featureListTest,trainingsetLabels,testsetLabels,"test")


def run ():

    #endpoint = "http://dbpedia.org/sparql"
    endpoint = "http://localhost:8891/sparql"
    # Main("http://dbpedia.org/sparql")
    # Main2("http://dbpedia.org/sparql")
    queries = []
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}","T1"))
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}","T2"))
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}","T3"))
    queries.append(("SELECT ?p COUNT(?o1) as ?o WHERE { <URI> ?p ?o1} GROUP BY ?p","N1"))
    queries.append(("SELECT ?p COUNT(?o2) as ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o2} GROUP BY ?p","N2"))

    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT ?p COUNT(?o1) as ?o WHERE { <URI> ?p ?o1} GROUP BY ?p","N1"))
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT ?p COUNT(?o2) as ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o2} GROUP BY ?p","N2"))
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT ?p COUNT(?o3) as ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o3 } GROUP BY ?p","N3"))
    Main("http://dbpedia.org/sparql",queries)


    queries = []
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}","T1"))
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}","T2"))
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}","T3"))
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}","T1"))
    queries.append(("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}","T2"))
    Main("http://dbpedia.org/sparql",queries)


run()