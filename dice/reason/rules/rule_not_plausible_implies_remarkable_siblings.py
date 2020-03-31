from dice.reason.rules import SiblingRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters


class RuleNotPlausibleImpliesRemarkableSiblings(SiblingRule):

    weight = Parameters.RULE_NOT_PLAUSIBLE_IMPLIES_REMARKABLE_SIBLINGS_WEIGHT

    def _ground(self, brother, sister, taxonomy_weight, similarity_weight):
        self.add(
            [Variable(brother, Dimensions.PLAUSIBLE), Variable(sister, Dimensions.REMARKABLE)],
            [Variable(sister, Dimensions.PLAUSIBLE)],
            taxonomy_weight=taxonomy_weight,
            similarity_weight=similarity_weight,
        )
