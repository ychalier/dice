from dice.constants import Parameters
from dice.kb import KnowledgeBase
from dice.kb import Fact
from dice.similarity import SimilarityMatrix
from dice.evidence import Entailer
from dice.evaluation import Tracker
from dice import Pipeline
import copy
import os


def slugify(text):
    import unidecode
    import re
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '-', text)


class KbExtender:

    MAX_NEIGHBORHOOD_NODES = 5
    MAX_NEIGHBORHOOD_FACTS = 1000


    def __init__(self, reference_inputs):
        self.reference_inputs = reference_inputs
        self.kb = reference_inputs.get_kb()
        self.taxonomy = reference_inputs.get_taxonomy()
        self.probability = reference_inputs.get_probability()
        self.similarity = reference_inputs.get_similarity_matrix()
        self.subjects = dict()
        for fact in self.kb.values():
            self.subjects.setdefault(fact.subject, list())
            self.subjects[fact.subject].append(fact)

    def _generate_candidates(self, subject, verbose=True):
        if verbose:
            print("Generating candidates...")
        known = set(map(lambda fact: fact.property, self.subjects[subject]))
        candidates = set()
        for neighbor in self.taxonomy.neighborhood(subject):
            for fact in self.subjects[neighbor]:
                joint = self.probability.joint(subject, fact.property)
                if fact.property in known or joint <= 0:
                    continue
                candidates.add(fact.property)
        kb = KnowledgeBase()
        for property in candidates:
            fact = Fact()
            fact.subject = subject
            fact.property = property
            fact.score = 0
            fact.source = Parameters.DUMMY_INJECTER_SOURCE
            fact.index = len(kb) + 1
            kb[fact.index] = fact
        return kb

    def _init_pipeline(self, folder, subject, candidates):
        pipeline = Pipeline(folder, {
            "embedder_partial_output_path": "embedder-tmp-" + slugify(subject) + ".tsv",
            "entailer_partial_output_path": "entailer-tmp-" + slugify(subject) + ".tsv",
        })
        kb = KnowledgeBase()
        for fact in list(self.subjects[subject]) + list(candidates.values()):
            copied_fact = copy.deepcopy(fact)
            copied_fact.index = len(kb) + 1
            kb[copied_fact.index] = copied_fact
        pipeline.set_kb(kb)
        return pipeline

    def _extend_inputs(self, subject, pipeline, verbose=True):
        if verbose:
            print("Extending inputs...")

        neighbor_facts = dict()
        if subject not in self.taxonomy.nodes:
            neighbors = set()
        else:
            parents = list(self.taxonomy.predecessors(subject))
            parents.sort(key=lambda v: -self.taxonomy.weight(subject, v))
            siblings = list(set(self.taxonomy.siblings(subject)).difference([subject]))
            siblings.sort(key=lambda v: -self.taxonomy.weight(subject, v))
            neighbors = set(parents[:KbExtender.MAX_NEIGHBORHOOD_NODES]).union(siblings[:KbExtender.MAX_NEIGHBORHOOD_NODES])
        for neighbor in neighbors:
            for fact in self.subjects.get(neighbor, list()):
                index = self.similarity.index[fact.property]
                neighbor_facts.setdefault(index, list())
                neighbor_facts[index].append(fact.index)

        pipeline_kb = pipeline.get_kb()
        horizontal_indices = [
            self.similarity.index[property]
            for property in set([
                fact.property
                for fact in pipeline_kb.values()
            ])
        ]
        vertical_indices = list(neighbor_facts.keys())
        matrix = self.similarity.matrix[horizontal_indices][:, vertical_indices]
        for i, j in zip(*matrix.nonzero()):
            if len(pipeline_kb) > KbExtender.MAX_NEIGHBORHOOD_FACTS:
                break
            for fact_index in neighbor_facts[vertical_indices[j]]:
                fact = copy.deepcopy(self.kb[fact_index])
                fact.index = len(pipeline_kb)
                pipeline_kb[fact.index] = fact
                if len(pipeline_kb) > KbExtender.MAX_NEIGHBORHOOD_FACTS:
                    break
        pipeline.set_kb(pipeline_kb)
        if verbose:
            print("Applying pipeline...")
            pipeline.process([2, 3, 4, 5, 6, 7, 8])
        else:
            pipeline.step_taxonomy()
            pipeline.step_embedder()
            pipeline.step_similarity_matrix()
            pipeline.step_probability()
            pipeline.step_entailer()
            pipeline.step_detective()
            pipeline.step_assigner()

    def _extract_tracker(self, pipeline, verbose=True):
        if verbose:
            print("Building tracker...")
        tracker = Tracker()
        tracker.build(pipeline)
        # for index in list(tracker.keys()):
        #     if tracker[index].source != Parameters.DUMMY_INJECTER_SOURCE:
        #         del tracker[index]
        return tracker

    def extend(self, subject, folder, verbose=True):
        if verbose:
            print("Extending '{}'".format(subject))
        candidates = self._generate_candidates(subject, verbose)
        if verbose:
            print("Adding", len(candidates), "facts.")
        if len(candidates) > 0:
            pipeline = self._init_pipeline(folder, subject, candidates)
            self._extend_inputs(subject, pipeline, verbose)
            tracker = self._extract_tracker(pipeline, verbose)
        else:
            pipeline = Pipeline(folder, dict())
            tracker = Tracker()
        if os.path.isfile("embedder-tmp-" + slugify(subject) + ".tsv"):
            os.system("rm " + "embedder-tmp-" + slugify(subject) + ".tsv")
        if os.path.isfile("entailer-tmp-" + slugify(subject) + ".tsv"):
            os.system("rm " + "entailer-tmp-" + slugify(subject) + ".tsv")
        return tracker
