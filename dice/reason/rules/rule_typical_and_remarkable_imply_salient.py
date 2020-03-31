from dice.reason.rules import ConceptRule
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleTypicalAndRemarkableImplySalient(ConceptRule):

    weight = Parameters.RULE_TYPICAL_AND_REMARKABLE_IMPLY_SALIENT_WEIGHT

    def _ground(self, fact):
        self.add(
            [Variable(fact, Dimensions.SALIENT)],
            [Variable(fact, Dimensions.TYPICAL), Variable(fact, Dimensions.REMARKABLE)],
            similarity_weight=1,
        )
