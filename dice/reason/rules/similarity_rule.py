from dice.reason.rules import RuleInterface
from dice.constants import Dimensions
from dice.constants import Parameters
from dice.reason import Variable

import numpy as np

class SimilarityRule(RuleInterface):

    weight = Parameters.RULE_SIMILARITY_WEIGHT

    def _ground(self, fact_x, fact_y, similarity_weight):
        for dimension in Dimensions.iter():
            self.add(
                [Variable(fact_x, dimension)],
                [Variable(fact_y, dimension)],
                similarity_weight=similarity_weight,
                taxonomy_weight=1.
            )

    def ground(self):
        kb = self.grounder.inputs.get_kb()
        similarity = self.grounder.inputs.get_similarity_matrix()
        for x in self.grounder.concepts:
            facts_x = dict()
            properties_x = list()
            for i, index in enumerate(self.grounder.concepts[x]):
                properties_x.append(similarity.index[kb[index].property])
                facts_x[i] = index
            submatrix = similarity.matrix[properties_x][:, properties_x]
            for i, j in zip(*submatrix.nonzero()):
                for dimension in Dimensions.iter():
                    self.add(
                        [Variable(facts_x[i], dimension)],
                        [Variable(facts_x[j], dimension)],
                        similarity_weight=submatrix[i, j],
                        taxonomy_weight=1.
                    )

    def combine_weights(rule_weight, similarity_weight, evidence_weight, taxonomy_weight):
        return rule_weight * similarity_weight
