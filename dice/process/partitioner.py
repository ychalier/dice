from sklearn.cluster import KMeans
import random
import math
import tqdm
import numpy as np
import multiprocessing as mp
import queue
import traceback

class Task:

    def __init__(self, subject):
        self.subject = subject

    def __call__(self, worker):
        taxonomy = worker.partitioner.taxonomy
        if self.subject not in taxonomy.nodes:
            neighbors = set()
        else:
            parents = list(taxonomy.predecessors(self.subject))
            parents.sort(key=lambda v: -taxonomy.weight(self.subject, v))
            siblings = list(set(taxonomy.siblings(self.subject)).difference([self.subject]).difference(parents))
            siblings.sort(key=lambda v: -taxonomy.weight(self.subject, v))
            neighbors = set(parents[:worker.partitioner.max_siblings]).union(siblings[:worker.partitioner.max_siblings])
        candidates = dict()
        for fact in worker.partitioner.kb.values():
            if fact.subject not in neighbors:
                continue
            candidates.setdefault(fact.property, list())
            candidates[fact.property].append(fact.index)
        partition = list()
        for cluster in worker.partitioner.clusterize_properties(self.subject):
            partition.append(worker.partitioner.populate_neighborhood(self.subject, cluster, candidates))
        return partition

class Worker(mp.Process):

    def __init__(self, q_in, q_out, partitioner):
        mp.Process.__init__(self)
        self.partitioner = partitioner
        self.q_in = q_in
        self.q_out = q_out

    def run(self):
        while True:
            task = self.q_in.get()
            if task is None:
                self.q_in.task_done()
                break
            result = None
            try:
                self.q_out.put(task(self))
            except Exception as e:
                print(traceback.format_exc())
            finally:
                self.q_in.task_done()

class Partitioner:

    def __init__(self, inputs, max_cluster_size, max_neighborhood_size, max_siblings):
        self.kb = inputs.get_kb()
        self.similarity_matrix = inputs.get_similarity_matrix()
        self.taxonomy = inputs.get_taxonomy()
        self.max_cluster_size = max_cluster_size
        self.max_neighborhood_size = max_neighborhood_size
        self.max_siblings = max_siblings

    def clusterize_properties(self, subject):
        properties = {
            self.similarity_matrix.index[fact.property]: fact.index
            for fact in self.kb.values()
            if fact.subject == subject
        }
        indices = list(properties.keys())
        if len(indices) < self.max_cluster_size:
            return [list(properties.values())]
        clusters = dict()
        if len(indices) > 50000:  # node 'people' from Quasimodo
            clusters[0] = list(properties.values())
        else:
            matrix = self.similarity_matrix.matrix[indices][:, indices]
            kmeans = KMeans(n_clusters=math.ceil(len(indices) / self.max_cluster_size))
            for i, label in zip(indices, kmeans.fit(matrix).labels_):
                clusters.setdefault(label, list())
                clusters[label].append(properties[i])
        for i in list(clusters.keys()):
            while len(clusters[i]) > self.max_cluster_size:
                clusters[max(clusters) + 1] = clusters[i][:self.max_cluster_size]
                del clusters[i][:self.max_cluster_size]
        return list(clusters.values())

    def populate_neighborhood(self, subject, cluster, candidates):
        indices = sorted([
            self.similarity_matrix.index[self.kb[index].property]
            for index in cluster
        ])
        matrix = self.similarity_matrix.matrix[indices]
        neighborhood = cluster[:]
        maximum_over_columns = np.ravel(matrix.max(axis=0).todense())
        sorted_properties = sorted(candidates, key=lambda property: maximum_over_columns[self.similarity_matrix.index[property]])
        facts = list()
        for property in sorted_properties[:self.max_neighborhood_size-len(neighborhood)]:
            facts += candidates[property]
        neighborhood += facts[:self.max_neighborhood_size-len(neighborhood)]
        return [len(cluster)] + neighborhood

    def process(self, n_jobs):
        subjects = set([fact.subject for fact in self.kb.values()])
        partition = list()
        queue_in = mp.JoinableQueue()
        queue_out = mp.Queue()
        jobs = [Worker(queue_in, queue_out, self) for _ in range(n_jobs)]
        for job in jobs:
            job.start()
        for subject in subjects:
            queue_in.put(Task(subject))
        for job in jobs:
            queue_in.put(None)
        for subject in tqdm.tqdm(subjects):
            partition += queue_out.get()
        return partition

    def save(self, partition, path):
        with open(path, "w") as file:
            for part in partition:
                file.write("\t".join(map(str, part)) + "\n")
