from dice.reason.rules import TaxonomyRule


class SiblingRule(TaxonomyRule):

    def iterator(self, mapping):
        if mapping not in self.grounder.taxonomy.nodes:
            return list()
        return self.grounder.taxonomy.siblings(mapping)
