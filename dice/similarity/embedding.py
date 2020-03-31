import matplotlib.pyplot as plt
import numpy as np

class Embedding:

    def __init__(self):
        self._map = dict()
        self._imap = dict()
        self._matrix = None

    def save(self, path):
        with open(path + ".tsv", "w") as file:
            for key, index in self._map.items():
                file.write("{}\t{}\n".format(key, index))
        np.save(path + ".npy", self._matrix)

    def load(self, path):
        with open(path + ".tsv") as file:
            lines = file.readlines()
        for line in lines:
            key, index = line.strip().split("\t")
            self.add_to_map(int(key), int(index))
        self._matrix = np.load(path + ".npy")

    def add_to_map(self, key, index):
        self._map[key] = index
        self._imap[index] = key

    def get_map(self, facts):
        return {fact: self._map[fact] for fact in facts}

    def slice(self, slice):
        return self._matrix[sorted(slice), :]

    def embed(self, key):
        if key not in self._map:
            raise Exception("No embedding found for {}".format(key))
        return self._matrix[self._map[key]]

    def draw(self, filename):
        sim = list(np.ravel(self._matrix @ self._matrix.T))
        a, b = -1., 1.
        values = sorted([(x-a)/(b-a) for x in sim])
        fig = plt.figure(figsize=(6, 6))
        fig.subplots_adjust(bottom=0.2)
        info = "95th percentile: {}".format(values[int(.95 * len(values))]) + "\n"
        info += "99th percentile: {}".format(values[int(.99 * len(values))])
        plt.hist(values, density=True, bins=20)
        plt.xlabel("Cosine Similarity Mapped to [0, 1]\n\n" + info)
        plt.ylabel("Density")
        plt.xlim(0, 1)
        plt.savefig(filename)
        plt.close()

    def log(self, filename, formatter):
        with open(filename, "w") as file:
            for a, i in self._map.items():
                for b, j in self._map.items():
                    if i >= j:
                        similarity = (self._matrix[i] @ self._matrix[j] + 1.) / 2.
                        file.write("{}\t{}\t{}\n".format(formatter(a), formatter(b), similarity))
