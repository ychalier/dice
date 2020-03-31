from dice.kb import Fact
from dice.constants import Data
from dice.kb import KnowledgeBaseBuilder
import re

class QuasimodoKb(KnowledgeBaseBuilder):

    def build(self):
        first = True
        with open(Data.quasimodo_kb) as file:
            for line in file.readlines():
                if first:
                    first = False
                    continue
                if line == "":
                    continue
                split = line.strip().split("\t")
                if not self.in_seeds(split[0]) or int(split[4]) == 1:
                    continue
                fact = Fact()
                fact.subject = split[0]
                fact.property = (
                    split[1].replace("hasProperty", "is").replace("_", " ")
                    + " "
                    + split[2]
                ).strip()
                fact.score = float(split[5])
                fact.text = fact.delimiter.join([
                    re.sub(r" x\d+", "", s)
                    for s in split[6].split(" // ")
                ])
                self.add_fact(fact)
