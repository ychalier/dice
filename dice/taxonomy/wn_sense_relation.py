from dice.taxonomy import EquivalenceRelationInterface

class WnSenseRelation(EquivalenceRelationInterface):

    def key(self, kb, fact):
        return kb[fact].sense
