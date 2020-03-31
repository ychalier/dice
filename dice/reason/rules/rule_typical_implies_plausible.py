from dice.reason.rules import ConceptRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters

class RuleTypicalImpliesPlausible(ConceptRule):

    weight = Parameters.RULE_TYPICAL_IMPLIES_PLAUSIBLE_WEIGHT

    def _ground(self, fact):
        self.add(
            [Variable(fact, Dimensions.PLAUSIBLE)],
            [Variable(fact, Dimensions.TYPICAL)],
            similarity_weight=1,
        )
