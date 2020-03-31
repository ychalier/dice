from dice import Pipeline
from dice.evaluation import Tracker
from dice.evaluation import PairEvaluator
from dice.misc import notify
from dice.process import BulkPipeline
from dice.process import BulkGatherer
from dice.constants import Parameters

from functools import reduce
import hyperopt
import pickle
import shutil
import os

class BulkTuner:

    BULK_TUNER_FOLDER = "out/bulk/tuner"

    def __init__(self, annotation_file, feature, inputs_folder, partition_file, n_jobs):
        self.annotation_file = annotation_file
        self.inputs_folder = inputs_folder
        self.partition_file = partition_file
        self.n_jobs = n_jobs
        partition = list()
        with open(partition_file) as file:
            for line in file.readlines():
                partition.append(list(map(int, line.strip().split("\t"))))
        def objective(args):
            pipeline = Pipeline(inputs_folder, args)
            Parameters.process(**args)
            if feature == "evidence":
                pipeline.load_detective()
                # pipeline.step_detective()
            if feature == "confidence":
                bulk_pipeline = BulkPipeline(inputs_folder, partition)
                if os.path.isdir(BulkTuner.BULK_TUNER_FOLDER):
                    shutil.rmtree(BulkTuner.BULK_TUNER_FOLDER)
                bulk_pipeline.process(BulkTuner.BULK_TUNER_FOLDER, int(n_jobs))
                del bulk_pipeline
                assignment = BulkGatherer(BulkTuner.BULK_TUNER_FOLDER).gather(False)
                pipeline.set_assignment(assignment)
            tracker = Tracker()
            tracker.build(pipeline)
            PairEvaluator.FEATURE = feature
            PairEvaluator.CONFIDENCE = .5
            print(PairEvaluator(self.annotation_file, tracker).evaluate(True))
            return PairEvaluator(self.annotation_file, tracker).evaluate()
        self.objective = objective
        self.choices = dict()

    def parse_space(self, args):
        space = dict()
        for arg in args.split(" "):
            param, rng = arg.split("=")
            if "-" in rng:
                low, high = list(map(float, rng.split("-")))
                space[param] = hyperopt.hp.uniform(param, low, high)
            elif "," in rng:
                values = list(map(float, rng.split(",")))
                space[param] = hyperopt.hp.choice(param, values)
                self.choices[param] = values
            else:
                space[param] = hyperopt.hp.choice(param, (float(rng),))
                self.choices[param] = [float(rng)]
        return space

    def optimize(self, args, max_evals=200, trials_file="trials.pickle"):
        space = self.parse_space(args)
        if os.path.isfile(trials_file):
            with open(trials_file, "rb") as file:
                trials = pickle.load(file)
        else:
            trials = hyperopt.Trials()
        best = hyperopt.fmin(
            self.objective,
            space,
            algo=hyperopt.tpe.suggest,
            max_evals=max_evals,
            trials=trials,
        )
        pickle.dump(trials, open(trials_file, "wb"))
        for param, values in self.choices.items():
            best[param] = values[best[param]]
        notify("Finished Processing", "Best parameters: {params}\nLosses: {loss}".format(
            params=best,
            loss=trials.losses(),
        ))
        return best
