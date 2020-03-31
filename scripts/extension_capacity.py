"""
usage: python extension_capacity.py <inputs-folder>
"""

from scipy import sparse
from tqdm import tqdm
import sys
import os
sys.path.insert(0, "../")
from dice import Inputs

if __name__ == "__main__":

    print("Kb extension computation")
    if len(sys.argv) != 2:
        print(__doc__)
        exit()
    inputs_folder = sys.argv[1]

    print("Loading...")
    inputs = Inputs(inputs_folder)
    print("\tLoading KB...")
    kb = inputs.get_kb()
    print("\tLoading taxonomy...")
    taxonomy = inputs.get_taxonomy()
    print("\tLoading probability...")
    probability = inputs.get_probability()

    print("Gathering properties...")
    properties = dict()
    for fact in tqdm(kb.values()):
        properties.setdefault(fact.subject, set())
        properties[fact.subject].add(probability.index_P[fact.property])

    print("Gathering scores...")
    scores = sparse.lil_matrix((len(probability.C), len(probability.P)))
    for subject, indices in tqdm(properties.items()):
        index_c = probability.index_C[subject]
        for index_p in indices:
            scores[index_c, index_p] = 1

    print("Gathering neighbors")
    neighbors_buffer = dict()
    for c1 in tqdm(probability.C):
        neighbors_buffer[probability.index_C[c1]] = taxonomy.neighborhood(c1)
    neighbors = sparse.lil_matrix((len(probability.C), len(probability.P)))
    for index_c, neighborhood in tqdm(neighbors_buffer.items()):
        for index_p in set([i for c in neighborhood for i in properties.get(c, list())]):
            neighbors[index_c, index_p] = 1

    print("\nNumber of new facts: ", probability.law.multiply(neighbors).nnz - scores.nnz, "\n")
