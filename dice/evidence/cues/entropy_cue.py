from dice.evidence.cues import CueInterface
from dice.constants import Parameters
import numpy as np
import tqdm
from scipy import sparse
import pickle
import multiprocessing as mp
import traceback
import queue

def entropy(n):
    if n == 0 or n == 1:
        return 0
    p = 1 / n
    q = 1 - p
    return - p * np.log(p) - q * np.log(q)

def information_gain(V, W):
    v, w = float(V), float(W)
    if w == 1 or v == 0:
        return 1
    return entropy(v) - w / v * entropy(w)

class Task:

    def __init__(self, subject, indices, maximum_size=50):
        self.subject = subject
        self.indices = indices
        self.maximum_size = maximum_size

    def __call__(self, worker):
        self.indices = [i for i in self.indices if i in worker.kb]
        out = dict()
        slice = list()
        if self.subject in worker.probability.index_C:
            slice.append(worker.probability.index_C[self.subject])
        if worker.taxonomy.has_node(self.subject):
            for neighbor in list(worker.taxonomy.siblings(self.subject)) + list(worker.taxonomy.predecessors(self.subject)):
                if len(slice) >= self.maximum_size:
                    break
                if neighbor not in worker.probability.index_C:
                    continue
                slice.append(worker.probability.index_C[neighbor])
        neighborhood = worker.probability.law[slice, :]
        index_P = {
            index: worker.probability.index_P[worker.kb[index].property]
            for index in self.indices
        }
        v = neighborhood.shape[0]
        for index in self.indices:
            w = neighborhood[:, index_P[index]].nnz
            out[index] = information_gain(v, w)
        return out

class Worker(mp.Process):

    def __init__(self, kb, taxonomy, probability, q_in, q_out):
        mp.Process.__init__(self)
        self.kb = kb
        self.taxonomy = taxonomy
        self.probability = probability
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


class EntropyCue(CueInterface):

    name = "entropy"

    def gather(self, inputs, verbose=True, n_jobs=40, **args):
        if n_jobs is None:
            n_jobs = max(1, mp.cpu_count() // 2)
        kb = inputs.get_kb()
        taxonomy = inputs.get_taxonomy()
        probability = inputs.get_probability()

        queue_in = mp.JoinableQueue()
        queue_out = mp.Queue()
        jobs = [
            Worker(kb, taxonomy, probability, queue_in, queue_out)
            for _ in range(n_jobs)
        ]
        for job in jobs:
            job.start()
        remaining = 0
        for subject, indices in taxonomy.relation._imap.items():
            remaining += 1
            queue_in.put(Task(
                subject,
                indices
            ))
        for job in jobs:
            queue_in.put(None)
        pbar = tqdm.tqdm(total=len(kb), disable=not verbose)
        while remaining > 0:
            try:
                out = queue_out.get(timeout=60)
                for index, ig in out.items():
                    self[index] = ig
                    pbar.update(1)
                remaining -= 1
            except queue.Empty:
                break
        pbar.close()
