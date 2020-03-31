import numpy as np
import os

from dice.misc import Output

class InputsException(Exception):

    def __init__(self, field):
        message = "'{}' field is accessed but not instantiated".format(field)
        Exception.__init__(self, message)

class Inputs(Output):

    KB_PATH = "kb.tsv"
    TAXONOMY_PATH = "taxonomy.zip"
    EMBEDDING_PATH = "embedding"
    SIMILARITY_MATRIX_PATH = "similarity"
    PROBABILITY_PATH = "probability"
    TRANSITION_PATH = "transition.npy"
    ENTAILER_PATH = "entailer.tsv"
    DETECTIVE_PATH = "detective.tsv"
    ASSIGNMENT_PATH = "assignment.tsv"

    def __init__(self, folder, load=False):
        Output.__init__(self, folder)
        self._kb = None
        self._taxonomy = None
        self._embedding = None
        self._similarity_matrix = None
        self._probability = None
        self._transition = None
        self._entailer = None
        self._detective = None
        self._assignment = None
        if load:
            self.load()

    def clone(self, clone_folder):
        inputs = Inputs(clone_folder)
        if self._kb is not None:
            inputs.set_kb(self._kb)
        if self._taxonomy is not None:
            inputs.set_taxonomy(self._taxonomy)
        if self._embedding is not None:
            inputs.set_embedding(self._embedding)
        if self._similarity_matrix is not None:
            inputs.set_similarity_matrix(self._similarity_matrix)
        if self._probability is not None:
            inputs.set_probability(self._probability)
        if self._transition is not None:
            inputs.set_transition(self._transition)
        if self._entailer is not None:
            inputs.set_entailer(self._entailer)
        if self._detective is not None:
            inputs.set_detective(self._detective)
        if self._assignment is not None:
            inputs.set_assignment(self._assignment)
        return inputs

    def merge_kb(self, index_offset, other):
        if self._kb is not None:
            if other._kb is not None:
                for fact in other._kb.values():
                    fact.index += index_offset
                    self._kb[fact.index] = fact
        else:
            self._kb = other._kb

    def merge_taxonomy(self, index_offset, other):
        if self._taxonomy is not None:
            if other._taxonomy is not None:
                for index, key in other._taxonomy.relation._map.items():
                    self._taxonomy.relation.map(index + index_offset, key)
                for u in other._taxonomy.nodes():
                    if self._taxonomy.has_node(u):
                        self._taxonomy.nodes[u].setdefault("weight", 0)
                        self._taxonomy.nodes[u]["weight"] += other._taxonomy.nodes[u].get("weight", 0)
                    else:
                        self._taxonomy.add_node(u, weight=other._taxonomy.nodes[u].get("weight", 0))
                for u, v in other._taxonomy.edges():
                    if self._taxonomy.has_edge(u, v):
                        pass
                    else:
                        self._taxonomy.add_edge(u, v, weight=other._taxonomy.get_edge_data(u, v).get("weight", 0))
        else:
            self._taxonomy = other._taxonomy

    def merge_embedding(self, index_offset, other):
        if self._embedding is not None:
            if other._embedding is not None:
                import numpy as np
                shape = self._embedding._matrix.shape[0]
                for key, index in other._embedding._map.items():
                    self._embedding.add_to_map(key + index_offset, index + shape)
                self._embedding._matrix = np.vstack((self._embedding._matrix, other._embedding._matrix))
        else:
            self._embedding = other._embedding

    def merge_detective(self, index_offset, other):
        if self._detective is not None:
            if other._detective is not None:
                from dice.evidence import EvidenceWrapper
                for cue_cls, cue_dict in other._detective.cues.items():
                    for index, value in cue_dict.items():
                        self._detective.cues[cue_cls][index + index_offset] = value
                for index in other._detective.keys():
                    self._detective[index + index_offset] = EvidenceWrapper(index + index_offset, self._detective.cues.values())
        else:
            self._detective = other._detective

    def merge(self, other):
        index_offset = 0
        if self._kb is not None:
            index_offset = max(self._kb.keys()) + 1
        self.merge_kb(index_offset, other)
        self.merge_taxonomy(index_offset, other)
        self.merge_embedding(index_offset, other)
        self.merge_detective(index_offset, other)

    def save(self):
        self.save_kb()
        self.save_taxonomy()
        self.save_embedding()
        self.save_similarity_matrix()
        self.save_probability()
        self.save_transition()
        self.save_entailer()
        self.save_detective()
        self.save_assignment()

    def load(self):
        self.load_kb()
        self.load_taxonomy()
        self.load_embedding()
        self.load_similarity_matrix()
        self.load_probability()
        self.load_transition()
        self.load_entailer()
        self.load_detective()
        self.load_assignment()

    def save_kb(self):
        if self._kb is not None:
            self._kb.export(self.path(self.KB_PATH))

    def save_taxonomy(self):
        if self._taxonomy is not None:
            self._taxonomy.save(self.path(self.TAXONOMY_PATH))

    def save_embedding(self):
        if self._embedding is not None:
            self._embedding.save(self.path(self.EMBEDDING_PATH))

    def save_similarity_matrix(self):
        if self._similarity_matrix is not None:
            self._similarity_matrix.save(self.path(self.SIMILARITY_MATRIX_PATH))

    def save_probability(self):
        if self._probability is not None:
            self._probability.save(self.path(self.PROBABILITY_PATH))

    def save_transition(self):
        if self._transition is not None:
            np.save(self.path(self.TRANSITION_PATH), self._transition)

    def save_entailer(self):
        if self._entailer is not None:
            self._entailer.save(self.path(self.ENTAILER_PATH))

    def save_detective(self):
        if self._detective is not None:
            self._detective.save(self.path(self.DETECTIVE_PATH))

    def save_assignment(self):
        if self._assignment is not None:
            self._assignment.save(self.path(self.ASSIGNMENT_PATH))

    def load_kb(self):
        if os.path.isfile(self.path(self.KB_PATH)):
            from dice.kb import KnowledgeBase
            self._kb = KnowledgeBase(self.path(self.KB_PATH))

    def load_taxonomy(self):
        if os.path.isfile(self.path(self.TAXONOMY_PATH)):
            from dice.taxonomy import Taxonomy
            self._taxonomy = Taxonomy()
            self._taxonomy.load(self.path(self.TAXONOMY_PATH))

    def load_embedding(self):
        if os.path.isfile(self.path(self.EMBEDDING_PATH + ".tsv"))\
            and os.path.isfile(self.path(self.EMBEDDING_PATH + ".npy")):
            from dice.similarity import Embedding
            self._embedding = Embedding()
            self._embedding.load(self.path(self.EMBEDDING_PATH))

    def load_similarity_matrix(self):
        if os.path.isfile(self.path(self.SIMILARITY_MATRIX_PATH + "_index.pickle"))\
            and os.path.isfile(self.path(self.SIMILARITY_MATRIX_PATH + "_matrix.npz")):
            from dice.similarity import SimilarityMatrix
            self._similarity_matrix = SimilarityMatrix()
            self._similarity_matrix.load(self.path(self.SIMILARITY_MATRIX_PATH))

    def load_probability(self):
        if os.path.isfile(self.path(self.PROBABILITY_PATH + "_sets.pickle"))\
            and os.path.isfile(self.path(self.PROBABILITY_PATH + "_law.npz")):
            from dice.evidence import Probability
            self._probability = Probability()
            self._probability.load(self.path(self.PROBABILITY_PATH))

    def load_transition(self):
        if os.path.isfile(self.path(self.TRANSITION_PATH)):
            self._transition = np.load(self.path(self.TRANSITION_PATH))

    def load_entailer(self):
        if os.path.isfile(self.path(self.ENTAILER_PATH)):
            from dice.evidence import Entailer
            self._entailer = Entailer(self)
            self._entailer.load(self.path(self.ENTAILER_PATH))

    def load_detective(self):
        if os.path.isfile(self.path(self.DETECTIVE_PATH)):
            from dice.evidence import Detective
            self._detective = Detective(self)
            self._detective.load(self.path(self.DETECTIVE_PATH))

    def load_assignment(self):
        if os.path.isfile(self.path(self.ASSIGNMENT_PATH)):
            from dice.reason import Assignment
            self._assignment = Assignment([])
            self._assignment.load(self.path(self.ASSIGNMENT_PATH))

    def get_kb(self):
        if self._kb is None:
            self.load_kb()
        if self._kb is None:
            raise InputsException("KB")
        return self._kb

    def get_taxonomy(self):
        if self._taxonomy is None:
            self.load_taxonomy()
        if self._taxonomy is None:
            raise InputsException("Taxonomy")
        return self._taxonomy

    def get_embedding(self):
        if self._embedding is None:
            self.load_embedding()
        if self._embedding is None:
            raise InputsException("Property embedding")
        return self._embedding

    def get_similarity_matrix(self):
        if self._similarity_matrix is None:
            self.load_similarity_matrix()
        if self._similarity_matrix is None:
            raise InputsException("Similarity matrix")
        return self._similarity_matrix

    def get_probability(self):
        if self._probability is None:
            self.load_probability()
        if self._probability is None:
            raise InputsException("Probability")
        return self._probability

    def get_transition(self):
        if self._transition is None:
            self.load_transition()
        if self._transition is None:
            raise InputsException("Transition")
        return self._transition

    def get_entailer(self):
        if self._entailer is None:
            self.load_entailer()
        if self._entailer is None:
            raise InputsException("Entailer")
        return self._entailer

    def get_detective(self):
        if self._detective is None:
            self.load_detective()
        if self._detective is None:
            raise InputsException("Detective")
        return self._detective

    def get_assignment(self):
        if self._assignment is None:
            self.load_assignment()
        if self._assignment is None:
            raise InputsException("Assignment")
        return self._assignment

    def set_kb(self, kb, save=True):
        self._kb = kb
        if save:
            self.save_kb()

    def set_taxonomy(self, taxonomy, save=True):
        self._taxonomy = taxonomy
        if save:
            self.save_taxonomy()

    def set_embedding(self, embedding, save=True):
        self._embedding = embedding
        if save:
            self.save_embedding()

    def set_similarity_matrix(self, similarity_matrix, save=True):
        self._similarity_matrix = similarity_matrix
        if save:
            self.save_similarity_matrix()

    def set_probability(self, probability, save=True):
        self._probability = probability
        if save:
            self.save_probability()

    def set_transition(self, transition, save=True):
        self._transition = transition
        if save:
            self.save_transition()

    def set_entailer(self, entailer, save=True):
        self._entailer = entailer
        if save:
            self.save_entailer()

    def set_detective(self, detective, save=True):
        self._detective = detective
        if save:
            self.save_detective()

    def set_assignment(self, assignment, save=True):
        self._assignment = assignment
        if save:
            self.save_assignment()
