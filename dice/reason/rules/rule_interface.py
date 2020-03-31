from dice.reason import Clause

import numpy as np

class RuleInterface:

    statistics = dict()

    def __init__(self, grounder, clauses):
        self.grounder = grounder
        self.clauses = clauses

    def cid(self):
        return len(self.clauses) + 1

    def add(self, positives, negatives, similarity_weight=None, evidence_weight=None, taxonomy_weight=None):
        if self.weight == 0.:
            return
        if similarity_weight is None:
            similarity_weight = self.get_similarity_weight(positives, negatives)
        if evidence_weight is None:
            evidence_weight = self.get_evidence_weight(positives, negatives)
        if taxonomy_weight is None:
            taxonomy_weight = self.get_taxonomy_weight(positives, negatives)
        self.clauses.append(Clause(
            self.cid(),
            positives,
            negatives,
            self.__class__,
            similarity_weight,
            evidence_weight,
            taxonomy_weight,
        ))
        self.statistics.setdefault(self.__class__, [0, 0])
        self.statistics[self.__class__][0] += 1
        self.statistics[self.__class__][1] += self.clauses[-1].get_weight()

    def get_similarity_weight(self, positives, negatives):
        return 1.

    def get_evidence_weight(self, positives, negatives):
        total = 0.
        for x in positives:
            w = self.grounder.detective[x.index][x.dimension]
            total = total + w - (total * w)
        for x in negatives:
            w = 1 - self.grounder.detective[x.index][x.dimension]
            total = total + w - (total * w)
        return total

    def get_taxonomy_weight(self, positives, negatives):
        return 1.

    def ground(self, grounder, clauses):
        raise NotImplementedError

    def combine_weights(rule_weight, similarity_weight, evidence_weight, taxonomy_weight):
        return rule_weight * similarity_weight * evidence_weight
