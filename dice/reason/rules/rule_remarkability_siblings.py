from dice.reason.rules import SiblingRule
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleRemarkabilitySiblings(SiblingRule):

    weight = Parameters.RULE_REMARKABILITY_SIBLINGS_WEIGHT

    def _ground(self, brother, sister, taxonomy_weight, similarity_weight):
        self.add(
            [],
            [Variable(brother, Dimensions.REMARKABLE), Variable(sister, Dimensions.REMARKABLE)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight,
        )
