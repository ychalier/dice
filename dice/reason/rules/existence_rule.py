from dice.reason.rules import RuleInterface
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class ExistenceRule(RuleInterface):

    weight = Parameters.RULE_EXISTENCE_WEIGHT

    def ground(self):
        for x in self.grounder.concepts:
            for p in [Dimensions.TYPICAL, Dimensions.SALIENT]:
                self.add(
                    [Variable(i, p) for i in self.grounder.concepts[x]],
                    [],
                    1.
                )

    def combine_weights(rule_weight, similarity_weight, evidence_weight, taxonomy_weight):
        return rule_weight
