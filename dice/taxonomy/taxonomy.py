import matplotlib.pyplot as plt
import networkx as nx
import decimal
import math
import os

from dice.taxonomy import EquivalenceRelationInterface
from dice.misc import Report
from dice.misc import Archive
from dice.constants import Parameters

def avg(iterable):
    return float(sum(iterable)) / len(list(iterable))

class Taxonomy(nx.classes.DiGraph):

    NODE_ATTRIBUTES = [(float, "weight")]
    EDGE_ATTRIBUTES = [(float, "weight")]

    def __init__(self):
        nx.classes.DiGraph.__init__(self)
        self.relation = EquivalenceRelationInterface()
        self.sibling_weights = None

    def __iadd__(self, other):
        for u in other.nodes():
            self.add_node(u, **other.node[u])
        for u, v in other.edges():
            self.add_edge(u, v, **self.get_edge_data(u, v))
        return self

    def _save_nodes(self, archive, path="nodes.tsv"):
        text = "node"
        if len(self.NODE_ATTRIBUTES) > 0:
            text += "\t" + "\t".join([a[1] for a in self.NODE_ATTRIBUTES])
        text += "\n"
        for u in self.nodes:
            text += u
            if len(self.NODE_ATTRIBUTES) > 0:
                for attr_type, attr_key in self.NODE_ATTRIBUTES:
                    text += "\t" + str(self.node[u][attr_key])
            text += "\n"
        archive.write(path, text)

    def _save_edges(self, archive, path="edges.tsv"):
        text = "start\tend"
        if len(self.EDGE_ATTRIBUTES) > 0:
            text += "\t" + "\t".join([a[1] for a in self.EDGE_ATTRIBUTES])
        text += "\n"
        for u, v in self.edges:
            text += u + "\t" + v
            if len(self.EDGE_ATTRIBUTES) > 0:
                for attr_type, attr_key in self.EDGE_ATTRIBUTES:
                    text += "\t" + str(self.get_edge_data(u, v)[attr_key])
            text += "\n"
        archive.write(path, text)

    def _save_relation(self, archive, path="map.tsv"):
        archive.write("map.tsv", self.relation.write())

    def save(self, path):
        archive = Archive(path, "w")
        self._save_nodes(archive)
        self._save_edges(archive)
        self._save_relation(archive)

    def _load_nodes(self, archive, path="nodes.tsv"):
        for line in archive.read(path).split("\n")[1:]:
            if line == "":
                continue
            split = line.strip().split("\t")
            self.add_node(split[0], **{
                self.NODE_ATTRIBUTES[i][1]: self.NODE_ATTRIBUTES[i][0](split[i+1])
                for i in range(len(self.NODE_ATTRIBUTES))
            })

    def _load_edges(self, archive, path="edges.tsv"):
        for line in archive.read(path).split("\n")[1:]:
            if line == "":
                continue
            split = line.strip().split("\t")
            self.add_edge(split[0], split[1], **{
                self.EDGE_ATTRIBUTES[i][1]: self.EDGE_ATTRIBUTES[i][0](split[i+2])
                for i in range(len(self.EDGE_ATTRIBUTES))
            })

    def _load_relations(self, archive, path="map.tsv"):
        self.relation.read(archive.read("map.tsv"))

    def load(self, path):
        archive = Archive(path)
        self._load_nodes(archive)
        self._load_edges(archive)
        self._load_relations(archive)

    def log_weights(self):
        if len(self.edges) == 0:
            return lambda e: 1.
        m = max([self.weight(u, v) for u, v in self.edges])
        return lambda e: math.log((math.e - 1) * self[e[0]][e[1]]["weight"] / m + 1)

    def fuse(self, other):
        self_weights = self.log_weights()
        other_weights = other.log_weights()
        merged = Taxonomy()
        merged.relation = self.relation
        for u in self.nodes:
            merged.add_node(u, weight=self.nodes[u]["weight"])
        for u, v in set(self.edges).union(set(other.edges)):
            if u in merged.nodes and v in merged.nodes:
                weight = 0
                if (u, v) in self.edges:
                    weight += Parameters.FUSE_ALPHA * self_weights((u, v))
                if (u, v) in other.edges:
                    weight += (1 - Parameters.FUSE_ALPHA) * other_weights((u, v))
                if weight < Parameters.FUSE_THRESHOLD:
                    continue
                merged.add_edge(u, v, weight=weight)
        return merged

    def community(self, root, direction="down", max_depth=None):
        community = Taxonomy()
        if root not in self.node():
            print("Root not found:", root)
            return community
        community.add_node(root, **self.node[root])
        buffer = [(0, root)]
        while len(buffer) > 0:
            depth, u = buffer.pop(0)
            neighbors = []
            if direction == "up":
                neighbors = self.predecessors(u)
            elif direction == "down":
                neighbors = self.successors(u)
            for v in neighbors:
                if v in community.nodes:
                    continue
                community.add_node(v, **self.node[v])
                if direction == "up":
                    community.add_edge(v, u, **self.get_edge_data(v, u))
                elif direction == "down":
                    community.add_edge(u, v, **self.get_edge_data(u, v))
                if v not in buffer and (max_depth is None or depth < max_depth):
                    buffer.append((depth + 1, v))
        return community

    def draw(self,
            path,
            rotation=0,
            size_attr="weight",
            node_color="xkcd:pastel orange",
            font_color="blue",
            font_size=13,
            custom_label=None,
            ):
        def stringify(x):
            if "." in str(x):
                return str(round(x, 2))
            elif x > 10000:
                return "{:.2E}".format(decimal.Decimal(x))
            return str(x)
        n = len(self.nodes())
        if n == 0:
            print("Could not draw taxonomy: empty.")
            return
        width, height = 4 * n / math.log(n + 1), 5 * math.log(n)
        plt.figure(figsize=(int(width), int(height)))
        plt.axis("off")
        pos = nx.drawing.nx_agraph.graphviz_layout(self, prog="dot")
        # plotting nodes
        if size_attr is not None:
            values = [float(self.node[u][size_attr]) for u in self.nodes]
            factor = float(n) * 300. / sum(values)
            node_size = [self.node[u][size_attr]*factor for u in self.nodes]
            nx.draw_networkx_nodes(
                    self,
                    pos,
                    node_color=node_color,
                    alpha=.8,
                    node_size=node_size)
        # plotting edges
        edge_labels = nx.get_edge_attributes(self, "weight")
        for key, value in edge_labels.items():
            edge_labels[key] = stringify(value)
        edge_widths = [edge_labels.get(edge, .3) for edge in self.edges]
        nx.draw_networkx_edges(
                self,
                pos,
                with_labels=False,
                width=edge_widths)
        nx.draw_networkx_edge_labels(self, pos, edge_labels=edge_labels)
        # plotting labels
        if custom_label is None:
            labels = {u: u for u in self.nodes}
            for attr_type, attr_key in self.NODE_ATTRIBUTES:
                for u in self.nodes:
                    labels[u] += "\n" + stringify(self.nodes[u][attr_key])
        else:
            labels = {u:custom_label(u) for u in self.nodes}
        text = nx.draw_networkx_labels(
                self,
                pos,
                labels=labels,
                font_color=font_color,
                font_size=font_size)
        for t in text.values():
            t.set_rotation(rotation)
        plt.savefig(path, format="svg")
        plt.close()

    def get_sibling_weight(self, u, v):
        if self.sibling_weights is None:
            from gensim.models import KeyedVectors
            import numpy as np
            from dice.constants import Data
            model = KeyedVectors.load(Data.word2vec_model_mmap, mmap="r")
            known_embeddings = dict()
            def embed(phrase):
                if phrase in known_embeddings:
                    return known_embeddings[phrase]
                dummy = np.zeros((300,))
                embed = np.zeros((300,))
                count = 0
                for word in phrase.split(" "):
                    if word in model:
                        count += 1
                        embed += model[word]
                if count > 0:
                    embed /= count
                norm = np.linalg.norm(embed)
                if norm > 0:
                    embed /= np.linalg.norm(embed)
                known_embeddings[phrase] = embed
                return embed
            def sim(phrase_a, phrase_b):
                embed_a = embed(phrase_a)
                embed_b = embed(phrase_b)
                return .5 * ((embed_a @ embed_b.T) + 1)
            self.sibling_weights = dict()
            for node in self.nodes:
                self.sibling_weights[node] = dict()
                for parent in self.predecessors(node):
                    weight_up = self.get_edge_data(parent, node)["weight"]
                    for sibling in self.successors(parent):
                        if sibling == node:
                            continue
                        weight_down = self.get_edge_data(parent, sibling)["weight"]
                        weight_sim = sim(node, sibling)
                        if weight_up == 0 or weight_down == 0 or weight_sim == 0:
                            weight_average = 0
                        else:
                            weight_average = 2 / (1/weight_up + 1/weight_down + 2/weight_sim)
                        if sibling in self.sibling_weights[node]:
                            self.sibling_weights[node][sibling] = max(weight_average, self.sibling_weights[node][sibling])
                        else:
                            self.sibling_weights[node][sibling] = weight_average
        return self.sibling_weights[u].get(v, 0.)

    def weight(self, u, v):
        if (u, v) in self.edges:
            return self.get_edge_data(u, v)["weight"]
        elif (v, u) in self.edges:
            return self.get_edge_data(v, u)["weight"]
        else:
            return self.get_sibling_weight(u, v)
        return 0.

    def roots(self):
        return set([
            u for u in self.nodes
            if len(list(self.predecessors(u))) == 0
        ])

    def leaves(self):
        return set([
            u for u in self.nodes
            if len(list(self.successors(u))) == 0
        ])

    def outliers(self):
        return self.roots().intersection(self.leaves())

    def siblings(self, u):
        out = set()
        for v in self.predecessors(u):
            for w in self.successors(v):
                out.add(w)
        return out.difference(set([u]))

    def neighborhood(self, u, remove_self=True):
        l = list()
        if u in self.nodes:
            l = list(set([u]).union(self.predecessors(u)).union(self.siblings(u)))
            l.sort(key=lambda v: -self.weight(u, v))
        else:
            l = [u]
        if remove_self and u in l:
            l.remove(u)
        return l
