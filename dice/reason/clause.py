from dice.reason import Assignment

class Clause:

    def __init__(self, cid, positives, negatives, rule, similarity_weight, evidence_weight, taxonomy_weight):
        self.id = cid
        self.rule = rule
        self.positives = positives
        self.negatives = negatives
        self.rule_weight = rule.weight
        self.similarity_weight = similarity_weight
        self.evidence_weight = evidence_weight
        self.taxonomy_weight = taxonomy_weight
        self.weight = None

    def __str__(self):
        return " or ".join([str(x) for x in self.positives] + ["not " + str(x) for x in self.negatives])

    def __contains__(self, var):
        return var in self.positives + self.negatives

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def get_weight(self):
        if self.weight is None:
            self.weight = self.rule.combine_weights(
                            self.rule_weight,
                            self.similarity_weight,
                            self.evidence_weight,
                            self.taxonomy_weight,
                        )
        return self.weight

    def is_unit(self, assignment):
        var = None
        for x in self.positives + self.negatives:
            if assignment[x] == Assignment.UNKNOWN:
                if var is None:
                    return False, None
                var = x
        return True, var

    def is_satisfied(self, assignment):
        for x in self.positives:
            if assignment[x] == Assignment.TRUE:
                return True
        for x in self.negatives:
            if assignment[x] == Assignment.FALSE:
                return True
        return False

    def to_tsv(self, kb, assignment):
        text = "\t".join(map(str, [
            self.id,
            self.rule.__name__,
            self.rule_weight,
            self.similarity_weight,
            self.evidence_weight,
            self.taxonomy_weight,
            self.get_weight()
        ]))
        vars = ""
        satisfied = False
        for x in self.positives:
            if assignment[x] == Assignment.TRUE:
                satisfied = True
                vars += "\t**" + x.to_tsv(kb) + "**"
            else:
                vars += "\t" + x.to_tsv(kb)
        for x in self.negatives:
            if assignment[x] == Assignment.FALSE:
                satisfied = True
                vars += "\t**not " + x.to_tsv(kb) + "**"
            else:
                vars += "\tnot " + x.to_tsv(kb)
        text += "\t{}{}".format(satisfied, vars)
        return text
