import pickle
import numpy as np
from scipy import sparse
from dice.constants import Parameters
from dice.misc import ProgressBar

class Probability:

    def __init__(self):
        self.C = None
        self.P = None
        self.law = None
        self.index_C = dict()
        self.index_P = dict()
        self.marginals_C = None
        self.marginals_P = None

    def build(self, inputs, verbose=True):
        kb = inputs.get_kb()
        self.C = list(set(map(lambda fact: fact.subject, kb.values())))
        indices_c = {self.C[i]: i for i in range(len(self.C))}
        similarity_matrix = inputs.get_similarity_matrix()
        indices_p = similarity_matrix.index
        self.P = sorted(indices_p, key=lambda p: similarity_matrix.index[p])
        self.law = dict()
        ppty_embedding = inputs.get_embedding()
        embedding = dict()
        corroboration_aux = dict()
        if verbose:
            bar = ProgressBar(len(kb))
            bar.start()
        corroboration = sparse.lil_matrix((len(self.C), len(self.P)))
        for index in kb:
            fact = kb[index]
            c = fact.subject
            p = fact.property
            corroboration[indices_c[c], indices_p[p]] = fact.score
            if p not in embedding:
                embedding[p] = ppty_embedding.embed(index)
            if verbose:
                bar.increment()
        if verbose:
            bar.stop()
        self.law = corroboration @ similarity_matrix.matrix
        del corroboration
        self.law /= self.law.sum()
        for i, c in enumerate(self.C):
            self.index_C[c] = i
        for j, p in enumerate(self.P):
            self.index_P[p] = j

    def save(self, path):
        data = {
            "C": self.C,
            "P": self.P
        }
        with open(path + "_sets.pickle", "wb") as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
        sparse.save_npz(path + "_law.npz", self.law)

    def load(self, path):
        with open(path + "_sets.pickle", "rb") as file:
            d = pickle.load(file)
        self.C = d["C"]
        self.P = d["P"]
        self.index_C = dict()
        self.index_P = dict()
        for i, c in enumerate(self.C):
            self.index_C[c] = i
        for j, p in enumerate(self.P):
            self.index_P[p] = j
        self.law = sparse.load_npz(path + "_law.npz")

    def joint(self, c, p):
        return float(self.law[self.index_C[c], self.index_P[p]])

    def marginal(self, key, value):
        if self.marginals_C is None or self.marginals_P is None:
            self.build_marginals()
        if key == "p":
            if self.marginals_P.ndim == 0:
                return self.marginals_P
            return self.marginals_P[self.index_P[value]]
        elif key == "c":
            if self.marginals_C.ndim == 0:
                return self.marginals_C
            return self.marginals_C[self.index_C[value]]

    def build_marginals(self):
        self.marginals_C = np.squeeze(np.asarray(self.law.sum(axis=1)))
        self.marginals_P = np.squeeze(np.asarray(self.law.sum(axis=0)))

    def conditional(self, key, c, p):
        if key == "p":
            denominator = self.marginal("p", p)
        elif key == "c":
            denominator = self.marginal("c", c)
        return self.joint(c, p) / denominator
