from dice.reason import Grounder
from dice.constants import Parameters

from contextlib import contextmanager
import gurobipy
import math
import sys
import os

@contextmanager
def silence_stdout():
    new_target = open(os.devnull, "w")
    old_target = sys.stdout
    sys.stdout = new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_target

class IlpGrounder(Grounder):

    model_name = "dice"

    def __init__(self, inputs, verbose=True):
        Grounder.__init__(self, inputs, verbose)

    def ground(self):
        Grounder.ground(self, include_evidence_rule=False)
        detective = self.inputs.get_detective()
        with silence_stdout():
            model = gurobipy.Model(self.model_name)
        if not self.verbose:
            model.Params.LogToConsole = 0
        gurobi_vars = dict()
        objective = gurobipy.LinExpr()
        for x in self.variables:
            y = model.addVar(
                lb=0.0,
                ub=1.0,
                vtype=gurobipy.GRB.CONTINUOUS,
                name=str(x)
            )
            objective += (detective[x.index][x.dimension] - Parameters.EVIDENCE_OFFSET) * y
            gurobi_vars[x] = y
        for i, clause in enumerate(self.clauses):
            if math.isnan(clause.get_weight()) or math.isinf(clause.get_weight()):
                continue
            z = model.addVar(
                lb=0.0,
                ub=1.0,
                vtype=gurobipy.GRB.CONTINUOUS,
                name="C({})".format(clause.id)
            )
            constraint = gurobipy.LinExpr()
            for x in clause.positives:
                constraint += gurobi_vars[x]
                model.addConstr(
                    z - gurobi_vars[x] >= 0,
                    name="X[C({}), {}]".format(clause.id, str(x))
                )
            for x in clause.negatives:
                constraint += (1 - gurobi_vars[x])
                model.addConstr(
                    z + gurobi_vars[x] >= 1,
                    name="Y[C({}), {}]".format(clause.id, str(x))
                )
            model.addConstr(
                constraint >= z,
                name="Z[C({}), {}]".format(
                    clause.id,
                    ", ".join(map(str, clause.positives + clause.negatives))[:128]
                )
            )
            objective -= (1 - z) * clause.get_weight()
        model.setObjective(objective, gurobipy.GRB.MAXIMIZE)
        return model
