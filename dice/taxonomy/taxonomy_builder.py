from dice.taxonomy import Taxonomy
from dice.constants import Parameters
import tqdm


class TaxonomyBuilder(Taxonomy):

    def __init__(self, inputs, relation_class):
        Taxonomy.__init__(self)
        self.relation = relation_class()
        self.inputs = inputs

    def merge(self, u, v):
        self.relation.merge(u, v)
        self.node[v]["weight"] += self.node[u]["weight"]
        for w in self.predecessors(u):
            if w != v and not self.has_edge(w, v):
                self.add_edge(w, v, weight=self.weight(w, u))
        for w in self.successors(u):
            if w != v and not self.has_edge(v, w):
                self.add_edge(v, w, weight=self.weight(u, w))
        self.remove_node(u)

    def _hypernyms(self, node):
        raise NotImplementedError

    def fill(self, verbose):
        if verbose:
            print("Filling taxonomy")
        for concept, facts in self.relation._imap.items():
            self.add_node(concept, weight=len(facts))
        nodes = set(self.nodes)
        for u in tqdm.tqdm(self.nodes, disable=not verbose):
            hypernyms = sorted([
                    (v, w)
                    for v, w in self._hypernyms(u)
                    if v in nodes
                ], key=lambda x: -x[1]
            )
            for v, w in hypernyms[:Parameters.TAXONOMY_BUILDER_MAX_RELATED]:
                # if v not in nodes: # or w < Parameters.TAXONOMY_BUILDER_EDGE_THRESHOLD:
                #     continue
                self.add_edge(v, u, weight=w)

    def prune(self, verbose):
        if verbose:
            print("Pruning lows")
        lows = [
            u for u in self.nodes
            if self.node[u]["weight"] < Parameters.TAXONOMY_BUILDER_LOWS_THRESHOLD
        ]
        for u in tqdm.tqdm(lows, disable=not verbose):
            w, weight = None, None
            for v in self.predecessors(u):
                if w is None or self.weight(v, u) > weight:
                    w = v
                    weight = self.weight(v, u)
            if w is None:
                for v in self.successors(u):
                    if w is None or self.weight(v, u) > weight:
                        w = v
                        weight = self.weight(v, u)
            if w is None:
                continue
            self.merge(u, w)

    def process(self, verbose=True):
        self.relation.fill(self.inputs.get_kb(), verbose)
        self.fill(verbose)
        # self.prune(verbose)
