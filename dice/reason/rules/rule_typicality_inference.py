from dice.reason.rules import RuleInterface
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters

class RuleTypicalityInference(RuleInterface):

    weight = Parameters.RULE_TYPICALITY_INFERENCE_WEIGHT

    def ground(self):
        for x in self.grounder.concepts:
            if x not in self.grounder.taxonomy.nodes:
                continue
            for p in self.grounder.properties[x]:
                negatives = []
                for y in self.grounder.taxonomy.successors(x):
                    if y not in self.grounder.properties:
                        continue
                    if p not in self.grounder.properties[y]:
                        continue
                    for child in self.grounder.properties[y][p]:
                        negatives.append(Variable(child, Dimensions.TYPICAL))
                if len(negatives) == 0:
                    continue
                for parent in self.grounder.properties[x][p]:
                    self.add([Variable(parent, Dimensions.TYPICAL)], negatives, similarity_weight=1)
