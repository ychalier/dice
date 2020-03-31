from dice.kb import Fact
from dice.kb import KnowledgeBase
from dice.reason import Variable
from dice.reason import Assignment
from dice.constants import Dimensions
from dice.misc import FileReader

import random
import codecs
import os

class TrackerFact(Fact):

    header = Fact.header + [
        "{dimension}_{field}".format(
            dimension=Dimensions.label(dimension, slug=True),
            field=field
        )
        for dimension in Dimensions.iter()
        for field in ["evidence", "assignment", "confidence"]
    ]

    def __init__(self):
        Fact.__init__(self)
        self.attributes = {
            dimension: {
                field: None
                for field in ["evidence", "assignment", "confidence"]
            }
            for dimension in Dimensions.iter()
        }

    def from_fact(fact):
        tracker_fact = TrackerFact()
        tracker_fact.index = fact.index
        tracker_fact.subject = fact.subject
        tracker_fact.property = fact.property
        tracker_fact.modality = fact.modality
        tracker_fact.score = fact.score
        tracker_fact.text = fact.text
        tracker_fact.sense = fact.sense
        tracker_fact.source = fact.source
        return tracker_fact

    def __str__(self):
        return Fact.__str__(self) + "\t" + "\t".join(
            str(self.attributes[dimension][field])
            for dimension in Dimensions.iter()
            for field in ["evidence", "assignment", "confidence"]
        )

    def parse(self, line):
        Fact.parse(self, line)
        split = line.strip().split("\t")
        i = 7
        for dimension in Dimensions.iter():
            for field in ["evidence", "assignment", "confidence"]:
                i += 1
                if i % 3 == 0:
                    self.attributes[dimension][field] = split[i] == "True"
                else:
                    self.attributes[dimension][field] = float(split[i])

class Tracker(KnowledgeBase):

    def __init__(self, path=None):
        self.evidence_rank = {d: dict() for d in Dimensions.iter()}
        self.confidence_rank = {d: dict() for d in Dimensions.iter()}
        KnowledgeBase.__init__(self, path)

    def save(self, path):
        with codecs.open(path + ".tmp", "w", "utf-8") as file:
            file.write("\t".join(TrackerFact.header) + "\n")
            for fact in self.values():
                file.write(str(fact) + "\n")
        os.rename(path + ".tmp", path)

    def load(self, path):
        def callback(line, *args):
            fact = TrackerFact()
            fact.parse(line)
            self[fact.index] = fact
        FileReader(path).read(callback, progress=False)
        self.build_ranks()

    def build(self, inputs):
        detective = inputs.get_detective()
        assignment = inputs.get_assignment()
        for dimension in Dimensions.iter():
            for fact in inputs.get_kb().values():
                if Variable(fact.index, dimension) not in assignment.map:
                    continue
                self.setdefault(fact.index, TrackerFact.from_fact(fact))
                self[fact.index].attributes[dimension]["evidence"] =\
                    detective[fact.index][dimension]
                self[fact.index].attributes[dimension]["assignment"] =\
                    assignment.map[Variable(fact.index, dimension)] == Assignment.TRUE
                self[fact.index].attributes[dimension]["confidence"] =\
                    assignment.confidence[Variable(fact.index, dimension)]
        self.build_ranks()

    def build_ranks(self):
        for dimension in Dimensions.iter():
            rank_evidence = sorted(
                self.keys(),
                key=lambda index: -self[index].attributes[dimension]["evidence"]
            )
            rank_confidence = sorted(
                self.keys(),
                key=lambda index: -self[index].attributes[dimension]["confidence"]
            )
            for i in range(len(rank_evidence)):
                self.evidence_rank[dimension][rank_evidence[i]] = i + 1
                self.confidence_rank[dimension][rank_confidence[i]] = i + 1
