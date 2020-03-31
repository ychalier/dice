from dice.reason.rules import SubconceptRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters

class RulePlausibilityInheritance(SubconceptRule):

    weight = Parameters.RULE_PLAUSIBILITY_INHERITANCE_WEIGHT

    def _ground(self, parent, child, taxonomy_weight, similarity_weight):
        self.add(
            [Variable(child, Dimensions.PLAUSIBLE)],
            [Variable(parent, Dimensions.PLAUSIBLE)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight,
        )
