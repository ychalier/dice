"""
Typicality, Salience and Remarkability are annotated with pair-wise preference.
Plausibility has to be annotated separately. This scripts takes a set of pairs
CSV files, split the pairs in two and outputs a CSV file of only facts, allowing
for plausibility assessment.

For cost reasons, facts are then grouped to have several on the same line, to
cover for judgement fees.

arguments: <output-path> <group-size> <in-paths>+

"""

import random
import sys
import os

def unfold(in_path):
    pairs = list()
    with open(in_path) as file:
        header = file.readline().replace("\ufeff", "").strip().split(",")
        for line in file.readlines():
            pairs.append({
                k: v
                for k,v in zip(header, line.strip().split(","))
            })
    facts = list()
    for pair in pairs:
        facts.append([pair["index_1"], pair["source_1"], pair["subject"], pair["property_1"]])
        facts.append([pair["index_2"], pair["source_2"], pair["subject"], pair["property_2"]])
    unique_facts = dict()
    for fact in facts:
        if (fact[0], fact[1]) not in unique_facts:
            unique_facts[(fact[0], fact[1])] = fact
    return list(unique_facts.values())

def group(facts, out_path, size):
    random.shuffle(facts)
    r = len(facts) % size
    if r != 0:
        facts += facts[:size-r]
    data = list()
    for i in range(0, len(facts), size):
        data.append(list())
        for j in range(size):
            data[i // size] += facts[i + j]
    with open(out_path, "w") as file:
        for i in range(size):
            if i > 0:
                file.write(",")
            file.write("index_{i},source_{i},subject_{i},property_{i}".format(i=i))
        file.write("\n")
        for row in data:
            file.write(",".join(row) + "\n")

if __name__ == "__main__":
    out_path, group_size, *in_paths = sys.argv[1:]
    facts = list()
    for in_path in in_paths:
        facts += unfold(in_path)
    group(facts, out_path, int(group_size))
