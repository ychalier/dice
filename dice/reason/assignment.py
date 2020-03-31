import matplotlib.pyplot as plt
import codecs

from dice.constants import Dimensions
from dice.reason import Variable
from dice.misc import Report

class Assignment:

    UNKNOWN = 0
    FALSE = 1
    TRUE = 2

    def __init__(self, variables):
        self.map = { x: self.UNKNOWN for x in variables }
        self.confidence = { x: -1. for x in variables }

    def __getitem__(self, variable):
        return self.map.setdefault(variable, self.UNKNOWN)

    def __str__(self):
        return "\n".join(map(lambda x: "{}: {}".format(str(x), "?FT"[self.map[x]]), self.map.keys()))

    def get_unassigned(self):
        return [x for x in self.map if self.map[x] == self.UNKNOWN]

    def assign(self, x, truth_value, confidence=None):
        self.map[x] = { True: self.TRUE, False: self.FALSE }[truth_value]
        if confidence is not None:
            self.confidence[x] = confidence
        else:
            self.confidence[x] = { True: 1., False: 0. }[truth_value]

    def group(self):
        grouped = dict()
        for x in self.map:
            if x.index not in grouped:
                grouped[x.index] = {d: self.UNKNOWN for d in Dimensions.iter()}
            grouped[x.index][x.dimension] = self.map[x]
        return grouped

    def save(self, path, kb=None):
        def format_fact(index):
            if kb is None: return index
            return repr(kb[index])
        def format_truth(value):
            if kb is None: return value
            return value == Assignment.TRUE
        grouped = self.group()
        with codecs.open(path, "w", "utf-8") as file:
            header = "fact\tplausible\ttypical\tremarkable\tsalient\t"
            header += "confidence_plausible\tconfidence_typical\t"
            header += "confidence_remarkable\tconfidence_salient\n"
            file.write(header)
            for index in grouped:
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    format_fact(index),
                    format_truth(grouped[index][Dimensions.PLAUSIBLE]),
                    format_truth(grouped[index][Dimensions.TYPICAL]),
                    format_truth(grouped[index][Dimensions.REMARKABLE]),
                    format_truth(grouped[index][Dimensions.SALIENT]),
                    self.confidence[Variable(index, Dimensions.PLAUSIBLE)],
                    self.confidence[Variable(index, Dimensions.TYPICAL)],
                    self.confidence[Variable(index, Dimensions.REMARKABLE)],
                    self.confidence[Variable(index, Dimensions.SALIENT)]))

    def log_true(self, path, kb, taxonomy):
        grouped = self.group()
        concepts = taxonomy.relation._imap
        with codecs.open(path, "w", "utf-8") as file:
            for concept in concepts:
                file.write("# " + concept + "\n\n")
                for d in Dimensions.iter():
                    file.write("## " + Dimensions.label(d) + "\n\n")
                    for index in concepts[concept]:
                        if grouped[index][d] == self.TRUE:
                            file.write("{}\t{}\n".format(
                                kb[index],
                                self.confidence[Variable(index, d)]
                            ))
                    file.write("\n")
                file.write("\n")

    def load(self, path):
        with open(path) as file:
            lines = file.readlines()
        for line in lines[1:]:
            index, p, t, r, s, cp, ct, cr, cs = line.strip().split("\t")
            self.map[Variable(int(index), Dimensions.PLAUSIBLE)] = int(p)
            self.map[Variable(int(index), Dimensions.TYPICAL)] = int(t)
            self.map[Variable(int(index), Dimensions.REMARKABLE)] = int(r)
            self.map[Variable(int(index), Dimensions.SALIENT)] = int(s)
            self.confidence[Variable(int(index), Dimensions.PLAUSIBLE)] = float(cp)
            self.confidence[Variable(int(index), Dimensions.TYPICAL)] = float(ct)
            self.confidence[Variable(int(index), Dimensions.REMARKABLE)] = float(cr)
            self.confidence[Variable(int(index), Dimensions.SALIENT)] = float(cs)

    def report(self, filename):
        counts = {
            d: {Assignment.TRUE: 0, Assignment.FALSE: 0}
            for d in Dimensions.iter()
        }
        for x, val in self.map.items():
            counts[x.dimension][val] += 1
        trues = [counts[d][Assignment.TRUE] for d in Dimensions.iter()]
        falses = [counts[d][Assignment.FALSE] for d in Dimensions.iter()]
        width = .4
        def pos(offset):
            return [i + offset * width for i in range(len(trues))]
        plt.figure(figsize=(8, 8))
        plt.bar(pos(0), trues, width, label="True")
        plt.bar(pos(1), falses, width, label="False")
        plt.xticks(pos(.5), [Dimensions.label(d) for d in Dimensions.iter()])
        plt.ylabel("Number of facts")
        plt.legend(loc="best")
        plt.savefig(filename, format="png")
        plt.close()
        report = Report()
        for d in Dimensions.iter():
            report.add_value_ratio(
                Dimensions.label(d),
                counts[d][Assignment.TRUE],
                counts[d][Assignment.TRUE] + counts[d][Assignment.FALSE]
            )
        return report

    def draw(self, kb, taxonomy, dimension, path):
        concepts = taxonomy.relation._imap
        def custom_label(u):
            scores = [
                (f, self.confidence[Variable(f, dimension)])
                for f in concepts.get(u, [])
            ]
            scores.sort(key=lambda x: -x[1])
            if len(scores) > 0:
                return u + "\n" + "\n".join(
                    [kb[s[0]].property
                     for s in scores[:3]])
            else:
                return u
        taxonomy.draw(path, custom_label=custom_label)
