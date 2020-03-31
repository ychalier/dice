import codecs
import json

from dice.constants import Data
from dice.taxonomy import TaxonomyBuilder
from dice.taxonomy import SubjectRelation

class ConceptNetTaxonomyBuilder(TaxonomyBuilder):

    def __init__(self, inputs):
        TaxonomyBuilder.__init__(self, inputs, SubjectRelation)
        self.links = dict()
        with codecs.open(Data.conceptnet_taxonomy, "r", "utf8") as file:
            self.links = json.load(file)

    def _hypernyms(self, node):
        if node not in self.links:
            return []
        return self.links[node]
