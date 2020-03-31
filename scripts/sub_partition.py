"""
In order to fasten the tuning of parameters, we only take into account clusters
that contains facts that will be later used in the evaluation pairs, i.e. that
are present in an evaluation file.

The confidence parameter allows for more fine-grained filtering: only pairs with
at least one dimension very clear are kept, allowing for more pruning.

arguments: <original-partition> <destination-partition> <annotation-file> <source> <confidence>
"""

import pandas as pd
import sys

if __name__ == "__main__":
    src_path, dest_path, annotation_file, source, confidence = sys.argv[1:]
    whitelist = set()
    confidence = float(confidence)
    df = pd.read_csv(annotation_file)
    df = df.where(df["source_1"] == source).dropna()
    df = df.where(
        (df["0"] >= 3 + confidence)
        | (df["0"] <= 3 - confidence)
        | (df["1"] >= 3 + confidence)
        | (df["1"] <= 3 - confidence)
        | (df["2"] >= 3 + confidence)
        | (df["2"] <= 3 - confidence)
        | (df["3"] >= 3 + confidence)
        | (df["3"] <= 3 - confidence)
    ).dropna()
    for index, row in df.iterrows():
        whitelist.add(row["index_1"])
        whitelist.add(row["index_2"])
    with open(dest_path, "w") as out_file:
        with open(src_path) as in_file:
            for line in in_file.readlines():
                n, *indices = list(map(int, line.strip().split("\t")))
                if len(whitelist.intersection(indices[:n])) > 0:
                    out_file.write(line)
