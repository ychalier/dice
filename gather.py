from gensim.models import KeyedVectors
from dice.constants.data import Data
import SPARQLWrapper
import requests
import zipfile
import json
import time

def generate_word2vec_mmap():
    print("Generating word2vec model")
    model = KeyedVectors.load_word2vec_format(Data.word2vec_model, binary=True)
    model.save(Data.word2vec_model_mmap)
    del model

def gather_webisalod_taxonomy(subjects):
    print("Gathering WebIsALOD taxonomy")
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
                ?concept rdfs:label "%(subject)s".
                ?hypernym rdfs:label ?hypernymLabel.
                ?g isaont:hasConfidence ?confidence.
            }
            ORDER BY DESC(?confidence)
            """ % {"subject":subject}
        )
        sparql.setReturnFormat(SPARQLWrapper.JSON)
        results = dict()
        for response in sparql.query().convert()["results"]["bindings"]:
            results[response["hypernymLabel"]["value"]] = \
                float(response["confidence"]["value"])
        return results
    hypernyms = dict()
    for i, subject in enumerate(subjects):
        print("\r{}/{}: '{}'".format(
            i+1,
            len(subjects),
            subject
        ) + " "*20, end="")
        results = query(subject)
        hypernyms[subject] = {
            hypernym: score
            for (hypernym, score) in results.items()
        }
    print("")
    with open(Data.webisalod, "w") as file:
        json.dump(hypernyms, file)

def gather_conceptnet_taxonomy(subjects):
    print("Gathering ConceptNet taxonomy")
    def extract(edge):
        return edge["end"]["term"][6:].replace("_", " "), edge["weight"]
    delay = 1.
    host = "http://api.conceptnet.io"
    route = "/query?start=/c/en/{subject}&rel=/r/IsA&limit=1000"
    hypernyms = dict()
    last_request = -1
    for i, subject in enumerate(subjects):
        if subject in hypernyms:
            continue
        if time.time() - last_request < delay:
            time.sleep(delay - time.time() + last_request)
        print("\r{}/{}: '{}'".format(
            i+1,
            len(subjects),
            subject
        ) + " "*20, end="")
        hypernyms[subject] = list(map(
            extract,
            requests
                .get(host + route.format(subject=subject.replace(" ", "_")))
                .json()["edges"]
        ))
        last_request = time.time()
    print("")
    with open(Data.conceptnet_taxonomy, "w") as file:
        json.dump(hypernyms, file)


if __name__ == "__main__":
    subjects = set()
    with zipfile.ZipFile("subjects.zip") as zip:
        with zip.open("subjects.txt") as file:
            subjects = set(file.read().decode("utf8").split("\n"))
    generate_word2vec_mmap()
    gather_webisalod_taxonomy(subjects)
    gather_conceptnet_taxonomy(subjects)
