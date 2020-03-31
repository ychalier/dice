from dice.reason import Assignment
from dice.reason import Variable
from dice.constants import Dimensions
from dice.constants import Parameters
from dice.misc import Report

def sign(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    return 0.

class Ilp:
    """
    Attributes and their signification @
    http://www.gurobi.com/documentation/8.1/refman/attributes.html#sec:Attributes
    """

    gurobi_log_file = "gurobi.log"
    vars_attrs = [
        "VarName",
        "VType",
        "LB",
        "UB",
        "Obj",
        "X",
        "Xn",
        "RC",
        "BarX",
        "Start",
        "VarHintVal",
        "VarHintPri",
        "BranchPriority",
        "Partition",
        "VBasis",
        "PStart",
        "IISLB",
        "IISUB",
        "PWLObjCvx",
        "SAObjLow",
        "SAObjUp",
        "SALBLow",
        "SALBUp",
        "SAUBLow",
        "SAUBUp",
        "UnbdRay",
    ]
    cstr_attrs = [
        "ConstrName",
        "Sense",
        "RHS",
        "Pi",
        "Slack",
        "CBasis",
        "DStart",
        "Lazy",
        "IISConstr",
        "SARHSLow",
        "SARHSUp",
        "FarkasDual",
    ]

    def __init__(self, variables, model, verbose=True):
        self.variables = variables
        self.model = model
        self.verbose = verbose
        self.assignment = None

    def solve(self, variables_path=None, constraints_path=None):
        open(self.gurobi_log_file, "w").close()
        self.model.params.Threads = 12
        self.model.optimize()
        self.assignment = Assignment(self.variables)
        f_vars, f_cstr = None, None
        if constraints_path is not None:
            f_cstr = open(constraints_path, "w")
            f_cstr.write("\t".join(Ilp.cstr_attrs) + "\n")
        if f_cstr is not None:
            for constraint in self.model.getConstrs():
                for attr in Ilp.cstr_attrs:
                    value = ""
                    try:
                        value = constraint.getAttr(attr)
                    except:
                        pass
                    f_cstr.write(str(value) + "\t")
                f_cstr.write("\n")
            f_cstr.close()
        if variables_path is not None:
            f_vars = open(variables_path, "w")
            f_vars.write("\t".join(Ilp.vars_attrs) + "\n")
        inner_confidence = []
        for gurobi_var in self.model.getVars():
            if gurobi_var.varName[0] not in "PTRS":
                continue
            if gurobi_var.rc == 0:
                up = min(2, gurobi_var.SAObjUp)
                low = max(-2, gurobi_var.SAObjLow)
                inner_confidence.append((gurobi_var.x - .51) * (up - low))
            if len(inner_confidence) == 0:
                a, b = 0, 1
            else:
                a, b = min(inner_confidence), max(inner_confidence)
        for gurobi_var in self.model.getVars():
            if f_vars is not None:
                for attr in Ilp.vars_attrs:
                    value = ""
                    try:
                        value = gurobi_var.getAttr(attr)
                    except:
                        pass
                    f_vars.write(str(value) + "\t")
                f_vars.write("\n")
            letter = gurobi_var.varName[0]
            if letter not in "PTRS":
                continue
            index = int(gurobi_var.varName[2:-1])
            confidence = 0
            if gurobi_var.rc != 0:
                confidence = gurobi_var.rc
            else:
                confidence = gurobi_var.x + gurobi_var.obj + Parameters.EVIDENCE_OFFSET
            self.assignment.assign(
                Variable(index, Dimensions.from_letter(letter)),
                gurobi_var.x >= .5,
                confidence,
            )
        if f_vars is not None:
            f_vars.close()
        return self.assignment

    def report(self):
        with open(self.gurobi_log_file) as file:
            text = file.read()
        report = Report()
        report.add(text)
        return report
