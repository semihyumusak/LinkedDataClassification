from feature_generator import Main

endpoint = "http://dbpedia.org/sparql"
#endpoint = "http://localhost:8891/sparql"
queries = []
queries.append("SELECT ?p ?o WHERE { <URI> ?p ?o}")
Main(endpoint,queries)

queries = []
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
Main(endpoint,queries)


queries = []
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}")
Main(endpoint,queries)

queries = []
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}")
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
Main(endpoint,queries)

queries = []
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p ?o}")
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p ?o}")
queries.append("SELECT DISTINCT ?p ?o WHERE { <URI> ?p1 ?o1. ?o1 ?p2 ?o2. ?o2 ?p ?o}")
Main(endpoint,queries)
