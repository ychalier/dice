from dice.reason.rules import RuleInterface

class ConceptRule(RuleInterface):

    def _ground(self, fact):
        raise NotImplementedError

    def ground(self):
        for x in self.grounder.concepts:
            for fact in self.grounder.concepts[x]:
                self._ground(fact)
