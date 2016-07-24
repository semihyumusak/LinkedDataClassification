
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

def populateFeatureAll (featDict, endpoint, queries):
    from feature_generator_functions import getAttributeWithoutCaching
    URI = featDict['uri']
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    #getAttributeWithoutCaching("SELECT ?p ?o WHERE { <"+featDict['uri']+"> ?p ?o}",featDict,endpoint)
    for query in queries:
        getAttributeWithoutCaching(query.replace("URI",URI),featDict,endpoint)



def Main(endpoint, queries):
    outFile = open('output.txt', 'a',encoding='utf-8')
    print ("---------------------------------------")
    outFile.write("---------------------------------------"+"\n")

    allqueriesstr= ""
    for query in queries:
        print(query)
        outFile.write(query+"\n")
        allqueriesstr += str(query)

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

    if os.path.isfile('dumps/testdump'+id):
        with open('dumps/testdump'+id,'rb') as f:
            featureListTest = pickle.load(f)
    else:
        for featDict in featureListTest:
            i= i+1
            # print(i)
            populateFeatureAll(featDict,endpoint,queries)

        with open('dumps/testdump'+id,'wb') as f:
            pickle.dump(featureListTest, f)


    if os.path.isfile('dumps/traindump'+id):
        with open('dumps/traindump'+id,'rb') as f:
            featureListTrain = pickle.load(f)
    else:
        # Populate Features
        for featDict in featureListTrain:
            i= i+1
            # print(i)
            populateFeatureAll(featDict,endpoint,queries)

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
    queries.append("SELECT ?p ?o WHERE { <URI> ?p ?o}")
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
    Main("http://dbpedia.org/sparql",queries)


    queries = []
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}")
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}")
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
    Main("http://dbpedia.org/sparql",queries)

    queries = []
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}")
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
    queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}")
    Main("http://dbpedia.org/sparql",queries)
