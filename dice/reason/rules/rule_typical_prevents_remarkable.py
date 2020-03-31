from dice.reason.rules import SubconceptRule
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleTypicalPreventsRemarkable(SubconceptRule):

    weight = Parameters.RULE_TYPICAL_PREVENTS_REMARKABLE_WEIGHT

    def _ground(self, parent, child, taxonomy_weight, similarity_weight):
        self.add(
            [],
            [Variable(child, Dimensions.REMARKABLE), Variable(parent, Dimensions.TYPICAL)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight
        )
