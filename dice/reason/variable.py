class Variable:

    def __init__(self, index, dimension):
        self.index = index
        self.dimension = dimension

    def __eq__(self, other):
        return self.index == other.index and self.dimension == other.dimension

    def __hash__(self):
        return hash(self.index)

    def __repr__(self):
        return "{}({})".format("PTRS"[self.dimension], self.index)

    def __str__(self):
        return "{}({})".format("PTRS"[self.dimension], self.index)

    def to_tsv(self, kb):
        return "{}({})".format("PTRS"[self.dimension], repr(kb[self.index]))
