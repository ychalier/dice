import codecs
import os

from dice.kb import Fact
from dice.misc import FileReader

class KnowledgeBase(dict):

    def __init__(self, path=None):
        super(KnowledgeBase, self).__init__()
        if path is not None:
            self.load(path)

    def save(self, path):
        with codecs.open(path + ".tmp", "w", "utf-8") as file:
            file.write("\t".join(Fact.header) + "\n")
            for fact in self.values():
                file.write(str(fact) + "\n")
        os.rename(path + ".tmp", path)

    def load(self, path):
        def callback(line, *args):
            fact = Fact()
            fact.parse(line)
            self[fact.index] = fact
        FileReader(path).read(callback, progress=False)

    def extract(self, indices):
        kb = KnowledgeBase()
        for index in indices:
            kb[index] = self[index]
        return kb

    def export(self, path, indices=None):
        if indices is None:
            indices = self.keys()
        kb = self.extract(indices)
        kb.save(path)

    def group_concepts_by_property(self, concepts):
        properties = dict()
        for concept in concepts:
            properties[concept] = dict()
            for index in concepts[concept]:
                if index not in self:
                    continue
                fact = self[index]
                property = fact.get_stemmed_property()
                properties[concept].setdefault(property, set()).add(index)
        return properties
