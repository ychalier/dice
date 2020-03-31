"""ConceptNet r/IsA scraper
usage:  python conceptnet.py kb_path cn.json
"""
import requests
import json
import time
import sys
import os

def extract(edge):
    return edge["end"]["term"][6:].replace("_", " "), edge["weight"]

def gather(output, subjects, delay=1., verbose=True):
    host = "http://api.conceptnet.io"
    route = "/query?start=/c/en/{subject}&rel=/r/IsA&limit=1000"
    cn = dict()
    if os.path.isfile(output):
        with open(output) as file:
            cn = json.load(file)
    last_request = -1
    for i, s in enumerate(subjects):
        if s in cn:
            continue
        if time.time() - last_request < delay:
            time.sleep(delay - time.time() + last_request)
        if verbose:
            print("({}/{})\tRequesting '{}'".format(i+1, len(subjects), s))
        try:
            cn[s] = list(map(
                extract,
                requests.get(host + route.format(subject=s)).json()["edges"]
            ))
            last_request = time.time()
            with open(output, "w") as file:
                json.dump(cn, file)
        except json.decoder.JSONDecodeError:
            print("Got a JSON error.")
    return cn

if __name__ == "__main__":
    kb_path, output, *inputs = sys.argv[1:]
    if len(inputs) == 0:
        inputs = set()
        with open(kb_path) as file:
            for line in file.readlines()[1:]:
                inputs.add(line.split("\t")[1].replace(" ", "_"))
    gather(output, inputs)
