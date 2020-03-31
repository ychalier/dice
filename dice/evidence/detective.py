import matplotlib.pyplot as plt
import numpy as np
import tqdm
import os

from dice.constants import Dimensions
from dice.kb import Fact
from dice.misc import FileReader
from dice.evidence import EvidenceWrapper
from dice.evidence import EvidenceDrawer
from dice.evidence.cues import *
from dice.misc import ProgressBar

class Detective(dict):

    def __init__(self, inputs):
        super(Detective, self).__init__()
        self.inputs = inputs
        self.cues = {
            EntropyCue: None,
            JointCue: None,
            NecessityCue: None,
            SufficiencyCue: None,
            ImplicationCue: None,
            ContradictionCue: None,
            EntailmentCue: None,
        }

    def build(self, verbose=True):
        for cls in self.cues:
            if verbose:
                print("Gathering", cls.__name__)
            self.cues[cls] = cls()
            self.cues[cls].gather(self.inputs, verbose=verbose, joint_cue=self.cues[JointCue])
        for index in self.inputs.get_kb():
            self[index] = EvidenceWrapper(index, self.cues.values())
        for dimension in Dimensions.iter():
            if verbose:
                print("Normalizing", Dimensions.label(dimension), "evidence")
            self.normalize(dimension, verbose)

    def normalize(self, dimension, verbose=True):
        groups = dict()
        for fact in self.inputs.get_kb().values():
            groups.setdefault(fact.subject, list())
            groups[fact.subject].append(fact.index)
        for group, facts in tqdm.tqdm(groups.items(), disable=not verbose):
            values = [self[index][dimension] for index in facts] # self.keys()]
            a, b = min(values), max(values)
            if a == b:
                if 0 <= a <= 1:
                    continue
                else:
                    a = 0
                    b *= 2
            for index in facts:
                self[index][dimension] = (self[index][dimension] - a) / (b - a)

    def save(self, path):
        cues_keys = sorted(self.cues, key=lambda cls: cls.name)
        with open(path, "w") as file:
            columns = [
                "index",
                "plausible",
                "typical",
                "remarkable",
                "salient",
            ] + list(map(lambda cls: cls.name, cues_keys))
            file.write("\t".join(columns) + "\n")
            for index in self.keys():
                file.write(("{" + "}\t{".join(columns) + "}\n").format(
                    index=index,
                    plausible=self[index].plausible,
                    typical=self[index].typical,
                    remarkable=self[index].remarkable,
                    salient=self[index].salient,
                    **{
                        cls.name: self.cues[cls].get(index, 0.)
                        for cls in cues_keys
                    }
                ))

    def load(self, path):
        cues_keys = sorted(self.cues, key=lambda cls: cls.name)
        for cls in self.cues:
            self.cues[cls] = cls()
        def callback(line, *args):
            index, p, t, r, s, *cues = line.strip().split("\t")
            for key, value in zip(cues_keys, cues):
                self.cues[key][int(index)] = float(value)
        FileReader(path).read(callback, progress=False)
        for index in self.inputs.get_kb():
            self[index] = EvidenceWrapper(index, self.cues.values())

    def log(self, path):
        self.save(path)
        kb = self.inputs.get_kb()
        with open(path) as file:
            lines = file.readlines()
        with open(path, "w") as file:
            file.write("index\tsubject\tproperty\t"
                + "\t".join(lines[0].split("\t")[1:]))
            for line in lines[1:]:
                index, *evidence = line.split("\t")
                file.write("\t".join([
                    index,
                    kb[int(index)].subject,
                    kb[int(index)].property
                ] + evidence))

    def plot(self, path):
        drawers = list()
        for dimension in Dimensions.iter():
            drawers.append(EvidenceDrawer(
                path + "-" + Dimensions.label(dimension, slug=True),
                {
                    index: self[index][dimension]
                    for index in self.inputs.get_kb()
                },
                Dimensions.label(dimension),
                self.inputs.get_kb(),
                self.inputs.get_taxonomy(),
            ))
        for cls in self.cues:
            drawers.append(EvidenceDrawer(
                path + "-" + cls.name,
                {
                    index: self.cues[cls][index]
                    for index in self.inputs.get_kb()
                },
                cls.name,
                self.inputs.get_kb(),
                self.inputs.get_taxonomy(),
            ))
        for drawer in drawers:
            drawer.top()
            drawer.distrib()
