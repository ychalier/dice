from dice.taxonomy import EquivalenceRelationInterface

class SubjectRelation(EquivalenceRelationInterface):

    def key(self, kb, fact):
        return kb[fact].subject
