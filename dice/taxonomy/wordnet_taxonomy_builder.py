from nltk.corpus import wordnet as wn

from dice.constants import Data
from dice.taxonomy import TaxonomyBuilder
from dice.taxonomy import WnSenseRelation

class WordnetTaxonomyBuilder(TaxonomyBuilder):

    def __init__(self, inputs):
        TaxonomyBuilder.__init__(self, inputs, WnSenseRelation)

    def _hypernyms(self, node):
        if node == "":
            return []
        return [
            (hypernym.name(), 1.)
            for hypernym in wn.synset(node).hypernyms()
        ]
