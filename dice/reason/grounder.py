import matplotlib.pyplot as plt
import pickle
import codecs

from dice.reason.rules import *
from dice.reason import Variable, Assignment
from dice.misc import Report
from dice.constants import Dimensions
from dice.constants import Parameters

class Grounder:

    rules = (
        RuleSalientImpliesPlausible,
        RuleTypicalImpliesPlausible,
        RuleTypicalAndRemarkableImplySalient,
        RulePlausibilityInheritance,
        RuleTypicalityInheritance,
        RulePlausibilityInference,
        RuleTypicalityInference,
        RuleRemarkabilityInheritance,
        RuleTypicalPreventsRemarkable,
        RuleNotPlausibleImpliesRemarkable,
        RuleNotPlausibleImpliesRemarkableSiblings,
        RuleRemarkabilitySiblings,
        RuleTypicalPreventsRemarkableSiblings,
        ExistenceRule,
        SimilarityRule,
    )

    header = [
        "clause_id",
        "grounded_rule",
        "rule_weight",
        "similarity_weight",
        "evidence_weight",
        "taxonomy_weight",
        "clause_weight",
        "satisfied",
        "variables+"
    ]

    def __init__(self, inputs, verbose=True):
        self.verbose = verbose
        self.inputs = inputs
        self.kb = inputs.get_kb()
        self.taxonomy = inputs.get_taxonomy()
        subjects = set([fact.subject for fact in self.kb.values()])
        # TODO: does not work with sense taxonomy!
        self.concepts = dict()
        for fact in self.kb.values():
            self.concepts.setdefault(fact.subject, list())
            self.concepts[fact.subject].append(fact.index)
        self.properties = self.kb.group_concepts_by_property(self.concepts)
        self.detective = inputs.get_detective()
        self.variables = []
        self.clauses = []
        ExistenceRule.weight = Parameters.RULE_EXISTENCE_WEIGHT
        RuleNotPlausibleImpliesRemarkableSiblings.weight = Parameters.RULE_NOT_PLAUSIBLE_IMPLIES_REMARKABLE_SIBLINGS_WEIGHT
        RuleNotPlausibleImpliesRemarkable.weight = Parameters.RULE_NOT_PLAUSIBLE_IMPLIES_REMARKABLE_WEIGHT
        RulePlausibilityInference.weight = Parameters.RULE_PLAUSIBILITY_INFERENCE_WEIGHT
        RulePlausibilityInheritance.weight = Parameters.RULE_PLAUSIBILITY_INHERITANCE_WEIGHT
        RuleRemarkabilityInheritance.weight = Parameters.RULE_REMARKABILITY_INHERITANCE_WEIGHT
        RuleRemarkabilitySiblings.weight = Parameters.RULE_REMARKABILITY_SIBLINGS_WEIGHT
        RuleSalientImpliesPlausible.weight = Parameters.RULE_SALIENT_IMPLIES_PLAUSIBLE_WEIGHT
        RuleTypicalAndRemarkableImplySalient.weight = Parameters.RULE_TYPICAL_AND_REMARKABLE_IMPLY_SALIENT_WEIGHT
        RuleTypicalImpliesPlausible.weight = Parameters.RULE_TYPICAL_IMPLIES_PLAUSIBLE_WEIGHT
        RuleTypicalPreventsRemarkableSiblings.weight = Parameters.RULE_TYPICAL_PREVENTS_REMARKABLE_SIBLINGS_WEIGHT
        RuleTypicalPreventsRemarkable.weight = Parameters.RULE_TYPICAL_PREVENTS_REMARKABLE_WEIGHT
        RuleTypicalityInference.weight = Parameters.RULE_TYPICALITY_INFERENCE_WEIGHT
        RuleTypicalityInheritance.weight = Parameters.RULE_TYPICALITY_INHERITANCE_WEIGHT
        SimilarityRule.weight = Parameters.RULE_SIMILARITY_WEIGHT

    def save(self, path):
        data = {
            "variables": self.variables,
            "clauses": self.clauses
        }
        with open(path, "wb") as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, path):
        with open(path, "rb") as file:
            data = pickle.load(file)
        self.variables = data["variables"]
        self.clauses = data["clauses"]

    def ground(self, include_evidence_rule=True):
        if self.verbose:
            print("Grounding...")
        for index in self.kb:
            for dimension in Dimensions.iter():
                self.variables.append(Variable(index, dimension))
        concepts_rules = (
            SimilarityRule(self, self.clauses),
        )
        subconcept_rules = (
            RulePlausibilityInheritance(self, self.clauses),
            RuleTypicalityInheritance(self, self.clauses),
            RulePlausibilityInference(self, self.clauses),
            RuleRemarkabilityInheritance(self, self.clauses),
            RuleTypicalPreventsRemarkable(self, self.clauses),
            RuleNotPlausibleImpliesRemarkable(self, self.clauses),
        )
        siblings_rules = (
            RuleNotPlausibleImpliesRemarkableSiblings(self, self.clauses),
            RuleRemarkabilitySiblings(self, self.clauses),
            RuleTypicalPreventsRemarkableSiblings(self, self.clauses),
        )
        other_rules = (
            RuleSalientImpliesPlausible,
            RuleTypicalImpliesPlausible,
            RuleTypicalAndRemarkableImplySalient,
            ExistenceRule,
        )
        kb = self.inputs.get_kb()
        similarity = self.inputs.get_similarity_matrix()
        concept_links = dict()
        parent_links = dict()
        siblings_links = dict()
        for x in self.concepts:
            for fact_x in self.concepts[x]:
                concept_links[fact_x] = set(self.concepts[x])
                parent_links[fact_x] = set()
                siblings_links[fact_x] = set()
            if x not in self.taxonomy.nodes:
                continue
            for child in self.taxonomy.successors(x):
                for fact_y in self.concepts.get(child, list()):
                    parent_links[fact_x].add(fact_y)
            for sibling in self.taxonomy.siblings(x):
                for fact_y in self.concepts.get(sibling, list()):
                    siblings_links[fact_x].add(fact_y)
        properties = dict()
        for fact in kb.values():
            ip = similarity.index[fact.property]
            properties.setdefault(ip, set())
            properties[ip].add(fact.index)
        inds = list(properties.keys())
        submatrix = similarity.matrix[inds][:, inds]
        for i, j in zip(*submatrix.nonzero()):
            similarity_weight = submatrix[i, j]
            for fact_x in properties[inds[i]]:
                for fact_y in properties[inds[j]].intersection(parent_links[fact_x]):
                    for rule in subconcept_rules:
                        rule._ground(fact_x, fact_y, 1., similarity_weight)
                for fact_y in properties[inds[j]].intersection(siblings_links[fact_x]):
                    for rule in siblings_rules:
                        rule._ground(fact_x, fact_y, 1., similarity_weight)
                for fact_y in properties[inds[j]].intersection(concept_links[fact_x]):
                    for rule in concepts_rules:
                        rule._ground(fact_x, fact_y, similarity_weight)
        for rule in other_rules:
            rule(self, self.clauses).ground()
        if include_evidence_rule:
            EvidenceRule(self, self.clauses).ground()
        return self.variables, self.clauses

    def full_report(self, path, assignment):
        with codecs.open(path, "w", "utf-8") as file:
            file.write("\t".join(Grounder.header) + "\n")
            for clause in self.clauses:
                file.write(clause.to_tsv(self.kb, assignment) + "\n")

    def report(self, clauses_path, assignment):
        report = Report()
        report.add_value("Variables", self.variables)
        report.add_value("Clauses", self.clauses)
        report.add_value("\nRule class", "counts/weights")
        for cls, (counts, weights) in RuleInterface.statistics.items():
            cls_name = str(cls)[str(cls).rfind(".") + 1:str(cls).rfind("'")]
            report.add_value(cls_name, "{}/{}".format(counts, weights))
        statistics = {True: [], False: []}
        statistics_detailed = dict()
        for c in self.clauses:
            satisfied = False
            for x in c.positives:
                if assignment[x] == Assignment.TRUE:
                    satisfied = True
                    break
            for x in c.negatives:
                if satisfied:
                    break
                if assignment[x] == Assignment.FALSE:
                    satisfied = True
            statistics[satisfied].append(c.get_weight())
            statistics_detailed.setdefault(c.rule, {True: [], False: []})[satisfied].append(c.get_weight())
        report.add_value_ratio("Unsatisfied clauses", statistics[False], self.clauses)
        for cls in self.rules:
            if cls not in statistics_detailed:
                continue
            report.add_value_ratio(
                "Unsatisfied clauses for {}".format(cls.__name__),
                statistics_detailed[cls][False],
                len(statistics_detailed[cls][True])
                    + len(statistics_detailed[cls][False])
            )
            plt.figure()
            plt.hist(statistics_detailed[cls][True], label="Satisfied", bins=20)
            plt.hist(statistics_detailed[cls][False], label="Unsatisfied", bins=20)
            plt.xlabel("Weight")
            plt.ylabel("Number of clauses")
            plt.title(cls.__name__)
            plt.legend()
            plt.savefig(clauses_path + "_{}.png".format(cls.__name__.lower()))
            plt.close()
        return report
