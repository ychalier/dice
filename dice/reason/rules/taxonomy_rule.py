from dice.reason.rules import RuleInterface
from dice.constants import Parameters
import numpy as np


class TaxonomyRule(RuleInterface):

    similarity_extenstion = True

    def _ground(self, parent, child):
        raise NotImplementedError

    def iterator(self, mapping):
        raise NotImplementedError

    def ground(self):
        kb = self.grounder.inputs.get_kb()
        similarity = self.grounder.inputs.get_similarity_matrix()
        for x in self.grounder.concepts:
            facts_x = dict()
            properties_x = list()
            for i, index in enumerate(self.grounder.concepts[x]):
                properties_x.append(similarity.index[kb[index].property])
                facts_x[i] = index
            for y in self.iterator(x):
                taxonomy_weight = self.grounder.taxonomy.weight(x, y)
                facts_y = dict()
                properties_y = list()
                for j, index in enumerate(self.grounder.concepts.get(y, list())):
                    properties_y.append(similarity.index[kb[index].property])
                    facts_y[j] = index
                submatrix = similarity.matrix[properties_x][:, properties_y]
                for i, j in zip(*submatrix.nonzero()):
                    self._ground(facts_x[i], facts_y[j], taxonomy_weight, submatrix[i, j])
