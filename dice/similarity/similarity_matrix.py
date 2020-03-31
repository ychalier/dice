from scipy import sparse
import pickle

class SimilarityMatrix:

    def __init__(self):
        self.matrix = None
        self.index = None

    def build(self, inputs, verbose=False):
        from dice.constants import Parameters
        from dice.misc import ProgressBar
        import numpy as np
        kb = inputs.get_kb()
        properties = list(set(map(lambda fact: fact.property, kb.values())))
        self.index = {properties[i]: i for i in range(len(properties))}
        embedding = inputs.get_embedding()
        indexed_embedding = dict()
        for index in kb:
            if kb[index].property not in indexed_embedding:
                indexed_embedding[kb[index].property] = embedding.embed(index)
        del embedding
        self.matrix = sparse.lil_matrix((len(properties), len(properties)))
        vect_q = np.array([indexed_embedding[q] for q in properties])
        if verbose:
            bar = ProgressBar(len(properties))
            bar.start()
        for i, p in enumerate(properties):
            vect_p = indexed_embedding[p]
            similarity = vect_p @ vect_q.T
            similarity += 1
            similarity /= 2
            slice = np.where(similarity > Parameters.SIMILARITY_THRESHOLD)
            self.matrix[i, slice] = similarity[slice]
            if verbose:
                bar.increment()
        if verbose:
            bar.stop()

    def save(self, path):
        index_file = path + "_index.pickle"
        matrix_file = path + "_matrix.npz"
        with open(index_file, "wb") as file:
            pickle.dump(self.index, file, protocol=pickle.HIGHEST_PROTOCOL)
        sparse.save_npz(matrix_file, self.matrix.tocsr())

    def load(self, path):
        index_file = path + "_index.pickle"
        matrix_file = path + "_matrix.npz"
        with open(index_file, "rb") as file:
            self.index = pickle.load(file)
        self.matrix = sparse.load_npz(matrix_file)
