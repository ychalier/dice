class ClauseSet:

    def __init__(self, variables, clauses):
        self.variables = variables
        self.clauses = clauses
        self.unassigned = dict()
        self.buckets = dict()
        self.pos = { var: set() for var in variables }
        self.neg = { var: set() for var in variables }
        self.unsatisfied = set()
        for clause in self.clauses:
            bucket = len(clause.positives + clause.negatives)
            if bucket not in self.unassigned:
                self.unassigned[bucket] = set()
            self.unassigned[bucket].add(clause)
            for var in clause.positives:
                self.pos[var].add(clause)
            for var in clause.negatives:
                self.neg[var].add(clause)
            self.unsatisfied.add(clause)
        for bucket in self.unassigned:
            for clause in self.unassigned[bucket]:
                self.buckets[clause] = bucket

    def __len__(self):
        return len(self.clauses)

    def __iter__(self):
        return iter(self.clauses)

    def update(self, x, truth_value):
        for clause in self.pos[x].union(self.neg[x]):
            bucket = self.buckets[clause]
            self.unassigned[bucket].remove(clause)
            if bucket - 1 not in self.unassigned:
                self.unassigned[bucket-1] = set()
            self.unassigned[bucket-1].add(clause)
            self.buckets[clause] = bucket - 1
        if truth_value:
            for clause in self.pos[x].intersection(self.unsatisfied):
                self.unsatisfied.remove(clause)
        else:
            for clause in self.neg[x].intersection(self.unsatisfied):
                self.unsatisfied.remove(clause)

    def get_occurences(self, x):
        return self.pos[x].union(self.neg[x])

    def get_pos_units(self, x):
        return self.pos[x].intersection(self.get_units())

    def get_neg_units(self, x):
        return self.neg[x].intersection(self.unsatisfied)

    def get_pos_unsatisfieds(self, x):
        return self.pos[x].intersection(self.get_units())

    def get_neg_unsatisfieds(self, x):
        return self.neg[x].intersection(self.unsatisfied)

    def get_unsatisfieds(self):
        return self.unsatisfied

    def get_units(self):
        return self.unassigned.setdefault(1, set())
