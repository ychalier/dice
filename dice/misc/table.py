class Table:

    def __init__(self, data):
        self.data = data
        self.n = len(self.data)
        self.p = len(self.data[0])
        self.column_sizes = None
        self.compute_column_sizes()

    def compute_column_sizes(self):
        self.column_sizes = []
        for j in range(self.p):
            self.column_sizes.append(max([
                len(self.data[i][j])
                for i in range(self.n)
            ]))

    def __str__(self):
        text = []
        for i in range(self.n):
            row = []
            for j in range(self.p):
                cell = self.data[i][j]
                gap = self.column_sizes[j] - len(cell)
                row.append(" " * (gap - gap // 2) + cell + " " * (gap // 2))
            text.append(" | ".join(row))
        text.insert(1, " | ".join(["-"*self.column_sizes[j] for j in range(self.p)]))
        return "\n".join(text)
