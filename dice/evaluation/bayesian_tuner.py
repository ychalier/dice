from dice import Pipeline
from dice.evaluation import Tracker
from dice.evaluation import PairEvaluator

from functools import reduce
import hyperopt
import pickle
import os

class BayesianTuner:

    def __init__(self, annotation_file, feature, *folders):
        self.annotation_file = annotation_file
        self.folders = folders
        def objective(args):
            trackers = list()
            for folder in self.folders:
                pipeline = Pipeline(
                    folder,
                    reduce(lambda x,y: dict(x, **y), (args, {"log": ""}))
                )
                pipeline.load()
                if feature == "evidence":
                    pipeline.step_detective()
                if feature == "confidence":
                    pipeline.step_assigner()
                tracker = Tracker()
                tracker.build(pipeline)
                trackers.append(tracker)
            PairEvaluator.FEATURE = feature
            return PairEvaluator(self.annotation_file, *trackers).evaluate()
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

    def optimize(self, args, max_evals=200):
        space = self.parse_space(args)
        if os.path.isfile("trials.pickle"):
            with open("trials.pickle", "rb") as file:
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
        pickle.dump(trials, open("trials.pickle", "wb"))
        for param, values in self.choices.items():
            best[param] = values[best[param]]
        return best
