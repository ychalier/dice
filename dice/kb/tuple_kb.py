from dice.kb import KnowledgeBaseBuilder
from dice.kb import Fact
from dice.constants import Data

def textify(pred):
    pred_map = {
        "has-part": "has a",
        "isa": "is a",
        "is-part-of": "is a part of"
    }
    if pred in pred_map:
        return pred_map[pred]
    return pred

class TupleKb(KnowledgeBaseBuilder):

    def build(self):
        with open(Data.tuple_kb) as file:
            header = file.readline().strip().split("\t")
            for line in file.readlines():
                if line == "":
                    continue
                statement = {
                    key: value
                    for key, value in zip(header, line.strip().split("\t"))
                }
                if not self.in_seeds(statement["Arg1"]):
                    continue
                fact = Fact()
                fact.subject = statement["Arg1"]
                fact.property = textify(statement["Pred"]) + " " + statement["Arg2"]
                fact.score = float(statement["QStrength"])
                fact.text = statement["Sentence"]
                self.add_fact(fact)
