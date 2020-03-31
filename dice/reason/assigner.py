import matplotlib.pyplot as plt
import os

from dice.taxonomy import Taxonomy
from dice.reason import Grounder
from dice.reason import IlpGrounder
from dice.reason import MaxSat
from dice.reason import Ilp
from dice.misc import Report
from dice.kb import KnowledgeBase
from dice.constants import Parameters

class Assigner:

    METHOD_SAT = 0
    METHOD_ILP = 1

    def __init__(self, inputs, verbose=False):
        self.verbose = verbose
        self.method = Parameters.ASSIGNMENT_METHOD
        self.inputs = inputs
        self.kb = inputs.get_kb()
        self.taxonomy = inputs.get_taxonomy()
        self.detective = inputs.get_detective()
        self.variables = None
        self.clauses = None
        self.grounder = None
        self.maxsat = None
        self.ilp = None
        self.model = None
        self.assignment = None

    def report(self, variable_path, assignment_path, grounder_path, clauses_path):
        usage = { x: 0 for x in self.variables}
        for c in self.clauses:
            for x in c.positives + c.negatives:
                usage[x] += 1
        plt.figure(figsize=(20, 6))
        x_min, x_max = 0, int(max(usage.values()))
        height =  [0 for _ in range(x_max-x_min+1)]
        for u in usage.values():
            height[u] += 1
        x = [i for i in range(x_min, x_max+1)]
        x_labels = []
        for i in range(x_min, x_max+1):
            if i in usage.values():
                x_labels.append(str(i))
            else:
                x_labels.append("")
        plt.bar(x, height)
        plt.xlabel("Number of clauses present in")
        plt.ylabel("Number of variables")
        plt.xticks(x, x_labels)
        plt.savefig(variable_path)
        plt.close()
        report = Report()
        report.merge(self.grounder.report(clauses_path, self.assignment))
        self.grounder.full_report(grounder_path, self.assignment)
        if self.method == self.METHOD_SAT:
            report.merge(self.maxsat.report())
        elif self.method == self.METHOD_ILP:
            report.merge(self.ilp.report())
        report.merge(self.assignment.report(assignment_path))
        return report

    def process(self, variables_path=None, constraints_path=None, free_memory=False):
        if self.method == self.METHOD_SAT:
            self.grounder = Grounder(self.inputs, verbose=self.verbose)
            self.variables, self.clauses = self.grounder.ground()
            self.maxsat = MaxSat(self.variables, self.clauses, verbose=self.verbose)
            # if free_memory:
            #     self.grounder.save("/tmp/grounder.pickle")
            #     del self.grounder
            self.assignment = self.maxsat.solve()
            # if free_memory:
            #     self.grounder = Grounder(self.inputs, verbose=self.verbose)
            #     self.grounder.load("/tmp/grounder.pickle")
        elif self.method == self.METHOD_ILP:
            self.grounder = IlpGrounder(self.inputs, verbose=self.verbose)
            self.model = self.grounder.ground()
            self.variables = self.grounder.variables
            self.clauses = self.grounder.clauses
            self.ilp = Ilp(self.variables, self.model, verbose=self.verbose)
            # if free_memory:
            #     self.grounder.save("/tmp/grounder.pickle")
            #     del self.grounder
            self.assignment = self.ilp.solve(variables_path, constraints_path)
            # if free_memory:
            #     self.grounder = IlpGrounder(self.inputs, verbose=self.verbose)
            #     self.grounder.load("/tmp/grounder.pickle")
        else:
            raise ValueError("Incorrect method '{}'".format(self.method))
        return self.assignment
