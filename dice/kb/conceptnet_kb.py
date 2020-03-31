from dice.kb import KnowledgeBaseBuilder
from dice.kb import Fact
from dice.constants import Data

def textify(relation):
    """
    https://github.com/commonsense/conceptnet5/wiki/Relations
    """
    return {
        "Antonym": "be an antonym of",
        "AtLocation": "be at",
        "CapableOf": "can",
        "Causes": "causes",
        "CausesDesire": "wants to",
        "CreatedBy": "be created by",
        "DefinedAs": "be defined as",
        "DerivedFrom": "be derived from",
        "Desires": "wants to",
        "DistinctFrom": "be different from",
        "FormOf": "be a form of",
        "HasA": "has",
        "HasContext": "has",
        "HasPrerequisite": "requires",
        "HasProperty": "be",
        "IsA": "be a",
        "LocatedNear": "be near",
        "MadeOf": "be made of",
        "MannerOf": "be a way to do",
        "MotivatedByGoal": "be motivated by",
        "ObstructedBy": "be obstructed by",
        "PartOf": "be a part of",
        "ReceivesAction": "can be",
        "RelatedTo": "be related to",
        "Synonym": "be a synonym of",
        "UsedFor": "be used to",
        "SimilarTo": "be similar to",
        "SymbolOf": "be a symbol of",
    }.get(relation, None)

class ConceptNetKb(KnowledgeBaseBuilder):

    def build(self):
        max_weight = 0
        with open(Data.conceptnet_kb) as file:
            for line in file.readlines():
                if line == "":
                    continue
                rel, subj, obj, weight = line.strip().split("\t")
                max_weight = max(max_weight, float(weight))
                if not self.in_seeds(subj) or rel == "IsA" or rel.startswith("Not"):
                    continue
                fact = Fact()
                fact.subject = subj
                if rel == "AtLocation" and obj.startswith("at "):
                    obj = obj[3:]
                if textify(rel) is None:
                    continue
                fact.property = (textify(rel) + " " + obj).strip()
                fact.score = float(weight)
                fact.text = " ".join(line.strip().split("\t")[:-1])
                self.add_fact(fact)
        for index in self:
            self[index].score /= max_weight
