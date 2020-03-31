from dice.reason.rules import TaxonomyRule


class SubconceptRule(TaxonomyRule):

    def iterator(self, mapping):
        if mapping not in self.grounder.taxonomy.nodes:
            return list()
        return self.grounder.taxonomy.successors(mapping)
