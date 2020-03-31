from dice.kb import KnowledgeBase

class KnowledgeBaseBuilder(KnowledgeBase):

    # List from https://en.wikipedia.org/wiki/English_modal_verbs
    modal_verbs = [
      "can",
      "could",
      "may",
      "might",
      "shall",
      "should",
      "must",
      "have to",
      "has to",
      "ought to",
      "had better",
      "need to",
      "dare to",
      "used to",
      "will",
      "would",
    ]

    modal_adverbs = [
        "always",
        "usually",
        "regularly",
        "normally",
        "often",
        "sometimes",
        "occasionally",
        "rarely",
        "seldom",
        "never",
    ]

    def __init__(self, source, *seeds):
        KnowledgeBase.__init__(self)
        self.source = source
        self.seeds = set(seeds)

    def in_seeds(self, subject):
        if len(self.seeds) == 1 and list(self.seeds)[0] == "*":
            return True
        return subject in self.seeds

    def add_fact(self, fact):
        fact.index = len(self) + 1
        fact.source = self.source
        self.extract_modality(fact)
        fact.property = fact.property.strip()
        self[fact.index] = fact

    def extract_modality(self, fact):
        for adverb in self.modal_adverbs:
            if adverb in fact.property:
                fact._add_modality(adverb)
                fact.property = fact.property.replace(adverb + " ", "")
        for verb in self.modal_verbs:
            if fact.property.startswith(verb):
                fact._add_modality(verb)
                fact.property = fact.property.replace(verb + " ", "")
