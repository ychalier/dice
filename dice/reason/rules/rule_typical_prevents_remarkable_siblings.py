from dice.reason.rules import SiblingRule
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleTypicalPreventsRemarkableSiblings(SiblingRule):

    weight = Parameters.RULE_TYPICAL_PREVENTS_REMARKABLE_SIBLINGS_WEIGHT

    def _ground(self, brother, sister, taxonomy_weight, similarity_weight):
        self.add(
            [],
            [Variable(brother, Dimensions.REMARKABLE), Variable(sister, Dimensions.TYPICAL)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight
        )
