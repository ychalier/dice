from dice.reason.rules import SubconceptRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters

class RulePlausibilityInference(SubconceptRule):

    weight = Parameters.RULE_PLAUSIBILITY_INFERENCE_WEIGHT

    def _ground(self, parent, child, taxonomy_weight, similarity_weight):
        self.add(
            [Variable(parent, Dimensions.PLAUSIBLE)],
            [Variable(child, Dimensions.TYPICAL)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight,
        )
