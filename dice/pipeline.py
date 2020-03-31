import datetime
import time
import os

from dice import Inputs
from dice.misc import Output
from dice.misc import Report
from dice.constants import Dimensions
from dice.constants import Parameters
from dice.misc import notify

class Pipeline(Inputs):

    parameters = {
        "logger_path": "log",
        "log": False,
        "kb_path": "data/kb.tsv",
        "entailer_batch_size": 100,
        "entailer_n_jobs": 2,
        "verbose": False,
        "notify": False,
        "embedder_partial_output_path": "embedder.tmp.tsv",
        "entailer_partial_output_path": "entailer.tmp.tsv",
    }

    def __init__(self, inputs_folder, parameters):
        Inputs.__init__(self, inputs_folder)
        # self.load()
        for key, value in parameters.items():
            if key in self.parameters:
                self.parameters[key] = value
        Parameters.process(**parameters)
        if "logger_path" in parameters:
            self.parameters["logger_path"] = parameters["logger_path"]
        if bool(self.parameters["log"]):
            self.logger = Output(os.path.join(inputs_folder, self.parameters["logger_path"]))

    def step_kb(self):
        from dice.kb import KnowledgeBase
        self.set_kb(KnowledgeBase(self.parameters["kb_path"]))

    def step_taxonomy(self):
        if Parameters.TAXONOMY_BUILDER == "wordnet":
            from dice.taxonomy import WordnetTaxonomyBuilder
            builder = WordnetTaxonomyBuilder(self)
        elif Parameters.TAXONOMY_BUILDER == "webisalod":
            from dice.taxonomy import WebisalodTaxonomyBuilder
            builder = WebisalodTaxonomyBuilder(self)
        elif Parameters.TAXONOMY_BUILDER == "conceptnet":
            from dice.taxonomy import ConceptNetTaxonomyBuilder
            builder = ConceptNetTaxonomyBuilder(self)
        elif Parameters.TAXONOMY_BUILDER == "merged":
            from dice.taxonomy import ConceptNetTaxonomyBuilder
            from dice.taxonomy import WebisalodTaxonomyBuilder
            conceptnet = ConceptNetTaxonomyBuilder(self)
            webisalod = WebisalodTaxonomyBuilder(self)
            conceptnet.process()
            webisalod.process()
            merged = conceptnet.fuse(webisalod)
            self.set_taxonomy(merged)
            if bool(self.parameters["log"]):
                merged.draw(self.logger.path("taxonomy.svg"))
            return
        builder.process(verbose=self.parameters["verbose"])
        self.set_taxonomy(builder)
        if bool(self.parameters["log"]):
            builder.draw(self.logger.path("taxonomy.svg"))

    def step_embedder(self):
        from dice.similarity import Embedder
        embedder = Embedder(self)
        embedder.process(verbose=self.parameters["verbose"], partial_output_path=self.parameters["embedder_partial_output_path"])
        self.set_embedding(embedder)
        if bool(self.parameters["log"]):
            embedder.draw(
                self.logger.path("similarity_distribution.png"))

    def step_similarity_matrix(self):
        from dice.similarity import SimilarityMatrix
        similarity_matrix = SimilarityMatrix()
        similarity_matrix.build(self, verbose=self.parameters["verbose"])
        self.set_similarity_matrix(similarity_matrix)

    def step_probability(self):
        from dice.evidence import Probability
        probability = Probability()
        probability.build(self, verbose=self.parameters["verbose"])
        self.set_probability(probability)

    def step_entailer(self):
        from dice.evidence import Entailer
        entailer = Entailer(self)
        entailer.process(
            batch_size=int(self.parameters["entailer_batch_size"]),
            n_jobs=int(self.parameters["entailer_n_jobs"]),
            verbose=self.parameters["verbose"],
            partial_output_path=self.parameters["entailer_partial_output_path"],
        )
        self.set_entailer(entailer)

    def step_detective(self):
        from dice.evidence import Detective
        detective = Detective(self)
        detective.build(verbose=self.parameters["verbose"])
        self.set_detective(detective)
        if bool(self.parameters["log"]):
            detective.log(self.logger.path("evidence.tsv"))
            detective.plot(self.logger.path("evidence"))

    def step_assigner(self):
        from dice.reason import Assigner
        assigner = Assigner(self, verbose=self.parameters["verbose"])
        if bool(self.parameters["log"]):
            self.set_assignment(assigner.process(
                variables_path=self.logger.path("gurobi_variables.tsv"),
                constraints_path=self.logger.path("gurobi_constraints.tsv")
            ))
        else:
            self.set_assignment(assigner.process())
        if bool(self.parameters["log"]):
            assigner.report(
                self.logger.path("variables_usage.png"),
                self.logger.path("assignment_stats.png"),
                self.logger.path("clauses.tsv"),
                self.logger.path("clauses")
            ).save(self.logger.path("report_assigner.txt"))
            self.get_assignment().save(
                self.logger.path("assignment.tsv"), self.get_kb())
            self.get_assignment().log_true(
                self.logger.path("assignment.txt"), self.get_kb(), self.get_taxonomy())
            for d in Dimensions.iter():
                self.get_assignment().draw(
                    self.get_kb(),
                    self.get_taxonomy(),
                    d,
                    self.logger.path("top-" + Dimensions.label(d, slug=True) + ".svg"),
                )

    def process(self, orders):
        steps = (
            ("Loading knowledge base", self.step_kb),
            ("Building taxonomy", self.step_taxonomy),
            ("Embedding facts", self.step_embedder),
            ("Computing similarity matrix", self.step_similarity_matrix),
            ("Computing probability", self.step_probability),
            ("Computing entailment", self.step_entailer),
            ("Computing evidence", self.step_detective),
            ("Assigning dimensions", self.step_assigner),
        )
        report = Report()
        report.add_value("folder", self.path(""))
        report.add("\nparameters")
        for key, value in self.parameters.items():
            report.add_value(key, value)
        for key, value in Parameters.__dict__.items():
            report.add_value(key, value)
        report.add("\nsteps")
        start, stop = min(orders), max(orders)
        last_checkpoint = time.time()
        for i, (name, method) in enumerate(steps):
            if i+1 not in orders:
                continue
            text = "\r{}/{}:\t{}...".format(i+1, stop, name)
            text += " " * (40 - len(text))
            print(text, end="")
            if self.parameters["verbose"]:
                print("")
            method()
            delta = datetime.timedelta(seconds=time.time()-last_checkpoint)
            if self.parameters["verbose"]:
                print("Done in", delta, "seconds.")
            report.add_value(method.__name__, str(delta))
            last_checkpoint = time.time()
        text = "\r{}/{}: Done.".format(stop, stop)
        text += " " * (40 - len(text))
        print(text)
        if self.parameters["log"]:
            report.save(self.logger.path("report_pipeline_{}.txt".format(int(time.time()))))
        if self.parameters["notify"]:
            notify("Finished Processing", str(report))
