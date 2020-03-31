from gensim.models import KeyedVectors
import numpy as np

from dice.similarity import Embedding
from dice.constants import Data
from dice.misc import ProgressBar

def stem(phrase):
    return phrase.lower()

class Embedder(Embedding):

    VECTOR_SHAPE = (300, )

    def __init__(self, inputs):
        Embedding.__init__(self)
        self.kb = inputs.get_kb()
        self.fact_formatter = lambda fact: fact.property
        idf = dict()
        total = 0.
        for index in self.kb:
            total += 1.
            for word in self.tokenize(index):
                idf.setdefault(word, 0.)
                idf[word] += 1.
        self.idf = {word: np.log(total/count) for word, count in idf.items()}

    def tokenize(self, index):
        return stem(self.fact_formatter(self.kb[index])).split(" ")

    def process(self, partial_output_path="embedder.tmp.tsv", verbose=True):
        matrix = []
        model = KeyedVectors.load(Data.word2vec_model_mmap, mmap="r")
        if verbose:
            bar = ProgressBar(len(self.kb))
            bar.start()
        for index in sorted(self.kb):
            vector = np.zeros(self.VECTOR_SHAPE)
            for word in self.tokenize(index):
                if word in model:
                    vector += self.idf.get(word, 1.) * model[word]
            if partial_output_path is not None:
                with open(partial_output_path, "a") as file:
                    file.write("{index}\t{vector}\n".format(
                        index=index,
                        vector=",".join(map(str, list(vector)))
                    ))
            else:
                self.add_to_map(index, len(matrix))
                matrix.append(vector)
            if verbose:
                bar.increment()
        if verbose:
            bar.stop()
        del model
        if partial_output_path is not None:
            with open(partial_output_path) as file:
                for line in file.readlines():
                    index, vector = line.strip().split("\t")
                    self.add_to_map(int(index), len(matrix))
                    matrix.append(np.array(list(map(float, vector.split(",")))))
        self._matrix = np.array(matrix)
        norm = np.linalg.norm(self._matrix, axis=1)
        norm[np.where(norm == 0)] += 1.
        self._matrix /= norm[:, None]
