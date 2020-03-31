from dice.reason.rules import SubconceptRule
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleRemarkabilityInheritance(SubconceptRule):

    weight = Parameters.RULE_REMARKABILITY_INHERITANCE_WEIGHT

    def _ground(self, parent, child, taxonomy_weight, similarity_weight):
        self.add(
            [],
            [Variable(child, Dimensions.REMARKABLE), Variable(parent, Dimensions.REMARKABLE)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight,
        )
