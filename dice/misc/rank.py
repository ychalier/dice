class Rank(list):

    METHOD_KENDALL = 0
    METHOD_SPEARMAN = 1

    def kendall(self, i, j):
        if self[j] > self[i]:
            return 1.
        elif self[j] == self[i]:
            return 0.
        return -1.

    def spearman(self, i, j):
        return self[j] - self[i]

    def score(self, method):
        if method == Rank.METHOD_KENDALL:
            function = self.kendall
        elif method == Rank.METHOD_SPEARMAN:
            function = self.spearman
        matrix = []
        for i in range(len(self)):
            matrix.append([])
            for j in range(len(self)):
                matrix[-1].append(function(i, j))
        return matrix

    def general_correlation_coefficient(self, other, method):
        a = self.score(method)
        b = other.score(method)
        x, y, z = 0., 0., 0.
        for i in range(len(a)):
            for j in range(len(b)):
                x += a[i][j] * b[i][j]
                y += a[i][j] ** 2
                z += b[i][j] ** 2
        return x / ((y * z) ** .5)

    def goodman_and_kruskal(self, other):
        concordant, reversed = 0., 0.
        for i in range(len(self)):
            for j in range(len(other)):
                order_self = self[i] - self[j]
                order_other = other[i] - other[j]
                if order_self * order_other > 0:
                    concordant += 1
                elif order_self * order_other < 0:
                    reversed += 1
        return (concordant - reversed) / (concordant + reversed)
