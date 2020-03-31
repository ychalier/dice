import codecs
import tqdm

class EquivalenceRelationInterface:

    def __init__(self):
        self._map = dict()
        self._imap = dict()

    def key(self, kb, fact):
        raise NotImplementedError

    def fill(self, kb, verbose=False):
        if verbose:
            print("Filling relation")
        for fact in tqdm.tqdm(kb, disable=not verbose):
            self.map(fact, self.key(kb, fact))

    def map(self, fact, key):
        self._map[fact] = key
        self._imap[key] = self._imap.get(key, []) + [fact]

    def merge(self, old_key, new_key):
        if old_key not in self._imap:
            return
        for fact in self._imap[old_key]:
            self.map(fact, new_key)
        del self._imap[old_key]

    def write(self):
        text = "fact\tkey\n"
        for fact, key in self._map.items():
            text += "{}\t{}\n".format(fact, key)
        return text

    def read(self, text):
        for line in text.split("\n")[1:]:
            if line == "":
                continue
            fact, key = line.strip().split("\t")
            self.map(int(fact), key)
