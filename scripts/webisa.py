"""
Usage: <kb-file> <output-json-path>
"""

import SPARQLWrapper
import tqdm
import json
import sys
sys.path.append("..")
from dice.kb import KnowledgeBase

def query(subject):
    endpoint = "http://webisa.webdatacommons.org/sparql"
    sparql = SPARQLWrapper.SPARQLWrapper(endpoint)
    sparql.setQuery("""
        PREFIX isaont: <http://webisa.webdatacommons.org/ontology#>
        SELECT ?concept ?hypernymLabel ?confidence
        WHERE{
            GRAPH ?g {
                ?concept skos:broader ?hypernym.
            }
            ?concept rdfs:label \"""" + subject + """\".
            ?hypernym rdfs:label ?hypernymLabel.
            ?g isaont:hasConfidence ?confidence.
        }
        ORDER BY DESC(?confidence)
        """
    )
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    results = dict()
    for response in sparql.query().convert()["results"]["bindings"]:
        results[response["hypernymLabel"]["value"]] = float(response["confidence"]["value"])
    return results

def query_all(subjects, whitelist):
    hypernyms = dict()
    for subject in tqdm.tqdm(subjects):
        results = query(subject)
        hypernyms[subject] = {
            hypernym: score
            for (hypernym, score) in results.items()
            if hypernym in whitelist
        }
    return hypernyms

if __name__ == "__main__":
    kb_path, output_path = sys.argv[1:]
    kb = KnowledgeBase(kb_path)
    subjects = set([fact.subject for fact in kb.values()])
    hypernyms = query_all(subjects, subjects)
    with open(output_path, "w") as file:
        json.dump(hypernyms, file)
