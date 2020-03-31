from dice.evaluation import Tracker
from dice.constants import Dimensions

import random as rd

def clean_property(fact):
    uncountables = set([
        "hate",
        "love",
        "hope",
        "humility",
        "selfishness",
        "conveyance",
        "coffee",
        "wine",
        "alcohol",
    ])
    countable = True
    if fact.subject in uncountables:
        countable = False
    ppty = fact.property
    replacement = "are"
    if not countable:
        replacement = "is"
    if ppty.startswith("be "):
        ppty = replacement + ppty[2:]
    return ppty.replace("hasProperty", replacement).replace("_", " ").strip()

class Pair:

    HEADER = [
        "subject",
        "index_1",
        "source_1",
        "property_1",
        "index_2",
        "source_2",
        "property_2",
    ]

    def __init__(self, tracker, i, j):
        if rd.random() < .5:
            i, j = j, i
        self.data = {
            "subject": tracker[i].subject,
            "index_1": str(i),
            "index_2": str(j),
            "property_1": clean_property(tracker[i]),
            "property_2": clean_property(tracker[j]),
            "source_1": tracker[i].source,
            "source_2": tracker[j].source,
        }

    def tsv(self):
        return "\t".join(self.data[key] for key in Pair.HEADER) + "\n"

class PairSampler:

    def __init__(self, tracker):
        self.tracker = tracker

    def process(self, path, amount):
        seed = rd.randint(1, 2**31-1)
        subjects = dict()
        for fact in self.tracker.values():
            subjects.setdefault(fact.subject, list())
            subjects[fact.subject].append(fact.index)
        rd.seed(seed)
        print("Random seed:", seed)
        pairs = [
            (i, j)
            for s in subjects
            for i in subjects[s]
            for j in subjects[s]
            if i > j
        ]
        weights = [
            sum([
                abs(self.tracker[i].attributes[d]["confidence"] - self.tracker[j].attributes[d]["confidence"]) / len(subjects[self.tracker[i].subject]) ** 1.5
                for d in Dimensions.iter()
            ])
            for i, j in pairs
        ]
        selection = list()
        while len(selection) < amount and len(pairs) > 0:
            choice = rd.choices(pairs, k=1, weights=weights)[0]
            index = pairs.index(choice)
            selection.append(Pair(self.tracker, *choice))
            pairs.pop(index)
            weights.pop(index)
        with open(path, "w") as file:
            file.write("\t".join(Pair.HEADER) + "\n")
            for pair in selection:
                file.write(pair.tsv())
