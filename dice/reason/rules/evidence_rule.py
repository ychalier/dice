from dice.reason.rules import ConceptRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters

class EvidenceRule(ConceptRule):

    weight = 1

    def _ground(self, fact):
        for dimension in Dimensions.iter():
            self.add(
                [Variable(fact, dimension)],
                [],
            )

    def combine_weights(rule_weight, similarity_weight, evidence_weight, taxonomy_weight):
        return rule_weight * (evidence_weight - Parameters.EVIDENCE_OFFSET)
