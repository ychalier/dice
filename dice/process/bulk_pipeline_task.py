from dice.misc import Output
from dice import Pipeline
import os

class BulkPipelineTask(Output):

    NEIGHBOR_THRESHOLD = 5000
    ABSOLUTE_THRESHOLD = 10000

    def __init__(self, folder, parameters, facts):
        Output.__init__(self, folder)
        self.parameters = parameters
        self.n_central_facts = facts[0]
        self.facts = facts[1:]

    def __call__(self, worker):
        if os.path.isfile(self.path("assignment.tsv")):
            return None
        if worker.verbose:
            print(os.getpid(), self.concept, len(facts))
        self.parameters["log"] = False
        pipeline = Pipeline(self.path(""), self.parameters)
        pipeline.set_kb(worker.inputs.get_kb().extract(self.facts), save=False)
        pipeline.set_taxonomy(worker.inputs.get_taxonomy(), save=False)
        pipeline.set_similarity_matrix(worker.inputs.get_similarity_matrix(), save=False)
        pipeline.set_detective(worker.inputs.get_detective(), save=False)
        pipeline.step_assigner()
        central_facts = self.facts[:self.n_central_facts]
        assignment = pipeline.get_assignment()
        for var in list(assignment.map.keys()):
            if var.index not in central_facts:
                del assignment.map[var]
        assignment.save(self.path("assignment.tsv"))
        del pipeline
        return None
