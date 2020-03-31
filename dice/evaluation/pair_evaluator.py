from dice.constants import Dimensions
import pandas as pd

class PairEvaluator:

    # GOLD_COLUMNS = {
    #     Dimensions.TYPICAL: "which_fact_is_more_typical_for_subjects",
    #     Dimensions.SALIENT: "which_fact_is_more_salient_for_subjects",
    #     Dimensions.REMARKABLE: "which_fact_is_more_remarkable_for_subjects"
    # }

    FEATURE = "confidence"
    CONFIDENCE = 1.0

    def __init__(self, annotation_file, *trackers):
        self.tracker = dict()
        for tracker_part in trackers:
            for fact in tracker_part.values():
                self.tracker[(fact.source, fact.index)] = fact
        # self.annotation = list()
        # with open(annotation_file) as file:
        #     header = file.readline().strip().split(",")
        #     for line in file.readlines():
        #         row = {
        #             key: value
        #             for key, value in zip(header, line.strip().split(","))
        #         }
        #         self.annotation.append(row)
        self.annotation = pd.read_csv(annotation_file)

    def predict(self, fact_1, fact_2, dimension):
        if self.FEATURE == "score":
            conf = lambda fact: fact.score
        else:
            conf = lambda fact: fact.attributes[dimension][self.FEATURE]
        if conf(fact_1) < conf(fact_2):
            return 2
        # if conf(fact_1) == conf(fact_2):
        #    return 1.5
        return 1

    def gold(self, row, dimension):
        if row[dimension] < 3:
            return 1
        return 2

    def loss(self, prediction, gold):
        return abs(float(prediction) - float(gold))

    def score(self, dimension, log=False):
        loss, count = 0., 0
        for index, row in self.annotation.iterrows():
            if abs(3 - row[dimension]) < self.CONFIDENCE:
                continue
            if (row["source_1"], int(row["index_1"])) not in self.tracker:
                continue
            if (row["source_2"], int(row["index_2"])) not in self.tracker:
                continue
            fact_1 = self.tracker[(row["source_1"], row["index_1"])]
            fact_2 = self.tracker[(row["source_2"], row["index_2"])]
            count += 1
            this_loss = self.loss(
                self.predict(fact_1, fact_2, dimension),
                self.gold(row, dimension),
            )
            if log and this_loss != 0:
                print("\t".join([
                    str(self.predict(fact_1, fact_2, dimension)),
                    str(self.gold(row, dimension)),
                    str(this_loss),
                    Dimensions.label(dimension),
                    repr(fact_1),
                    repr(fact_2),
                ]))
            loss += this_loss
        return loss, count

    def evaluate(self, details=False, log=False):
        results = dict()
        total_loss, total_count = 0., 0
        for dimension in Dimensions.iter():
            loss, count = self.score(dimension, log)
            if count == 0:
                count = 1
            results[dimension] = {
                "mae": loss / count,
                "n": count,
            }
            total_loss += loss
            total_count += count
        results[-1] = {
            "mae": total_loss / total_count,
            "n": total_count,
        }
        if details:
            return results
        return total_loss / total_count
