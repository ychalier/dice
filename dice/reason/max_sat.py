from dice.reason import Assignment
from dice.reason import ClauseSet
from dice.misc import ProgressBar
from dice.misc import Report

class MaxSat:

    def __init__(self, variables, clauses, verbose=True):
        self.verbose = verbose
        self.variables = variables
        self.clauses = ClauseSet(variables, clauses)
        self.assignment = Assignment(variables)
        self.queue = self.variables[:]
        self.counts = [dict(), dict()]

    def update_counts(self, mask=None):
        clauses = self.clauses.get_units()
        if mask is not None:
            clauses = clauses.intersection(mask)
        for x in self.assignment.get_unassigned():
            self.counts[1][x] = 0.
            self.counts[0][x] = 0.
            for c in clauses:
                if x in c.positives:
                    self.counts[1][x] += c.get_weight()
                if x in c.negatives:
                    self.counts[0][x] += c.get_weight()

    def update_queue(self):
        self.queue.sort(key=lambda x: abs(self.counts[1][x]-self.counts[0][x]))

    def find_safe_var(self):
        for x in self.assignment.get_unassigned():
            for truth_value in [True, False]:
                if truth_value:
                    units = self.clauses.get_pos_units(x)
                    unsatisfieds = self.clauses.get_neg_unsatisfieds(x)
                else:
                    units = self.clauses.get_neg_units(x)
                    unsatisfieds = self.clauses.get_pos_unsatisfieds(x)
                confidence = sum([c.get_weight() for c in units]) - sum([c.get_weight() for c in unsatisfieds])
                if confidence >= 0:
                    return x, truth_value, {True: 1., False:-1.}[truth_value] * confidence
        return None, None, None

    def solve(self):
        self.update_counts()
        self.update_queue()
        if self.verbose:
            bar = ProgressBar(len(self.queue))
            print("Starting reasoning...")
            bar.start()
        while len(self.queue) > 0:
            x = self.queue.pop()
            if self.verbose:
                bar.increment()
            self.assignment.assign(x, self.counts[1][x] > self.counts[0][x], self.counts[1][x] - self.counts[0][x])
            self.clauses.update(x, self.counts[1][x] > self.counts[0][x])
            while True:
                safe_var, truth_value, confidence = self.find_safe_var()
                if safe_var is None:
                    break
                self.assignment.assign(safe_var, truth_value, confidence)
                self.clauses.update(safe_var, truth_value)
                self.queue.remove(safe_var)
                if self.verbose:
                    bar.increment()
            self.update_counts(self.clauses.get_occurences(x))
            self.update_queue()
        if self.verbose:
            bar.stop()
        return self.assignment

    def report(self):
        report = Report()
        unsatisfieds = self.clauses.get_unsatisfieds()
        n_clauses = len(self.clauses)
        n_satisfieds = n_clauses - len(unsatisfieds)
        w_total = sum([c.get_weight() for c in self.clauses])
        w_satisfieds = w_total - sum([c.get_weight() for c in unsatisfieds])
        report.add_value_ratio("Satisfied weight", w_satisfieds, w_total)
        report.add_value_ratio("Satisfied clauses", n_satisfieds, n_clauses)
        return report
