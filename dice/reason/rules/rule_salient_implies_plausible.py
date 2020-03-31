from dice.reason.rules import ConceptRule
from dice.constants import Dimensions
from dice.reason import Variable
from dice.constants import Parameters

class RuleSalientImpliesPlausible(ConceptRule):

    weight = Parameters.RULE_SALIENT_IMPLIES_PLAUSIBLE_WEIGHT

    def _ground(self, fact):
        self.add(
            [Variable(fact, Dimensions.PLAUSIBLE)],
            [Variable(fact, Dimensions.SALIENT)],
            similarity_weight=1
        )
