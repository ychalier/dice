from allennlp.predictors.decomposable_attention import DecomposableAttentionPredictor
import codecs
import sys
import os
from dice.misc import ProgressBar
from contextlib import contextmanager

@contextmanager
def silence_stderr():
    new_target = open(os.devnull, "w")
    old_target = sys.stderr
    sys.stderr = new_target
    try:
        yield new_target
    finally:
        sys.stderr = old_target

from dice.constants import Data

import multiprocessing as mp
import traceback
import queue

class Task:

    def __init__(self, batch):
        self.batch = batch

    def __call__(self, worker):
        out = list()
        for i, result in enumerate(worker.predictor.predict_batch_json(self.batch)):
            out.append({
                "index": self.batch[i]["index"],
                "premise": self.batch[i]["premise"],
                "hypothesis": self.batch[i]["hypothesis"],
                "entailment": result["label_probs"][0],
                "contradiction": result["label_probs"][1],
                "neutral": result["label_probs"][2],
            })
        return out

class Worker(mp.Process):

    def __init__(self, q_in, q_out):
        mp.Process.__init__(self)
        self.predictor = None
        self.q_in = q_in
        self.q_out = q_out

    def run(self):
        with silence_stderr():
            self.predictor = DecomposableAttentionPredictor.from_path(
                archive_path=Data.attention_model
            )
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

class Entailer:

    """ Pre-trained models available at:
    https://github.com/allenai/allennlp/blob/master/MODELS.md
    """

    def __init__(self, inputs):
        self.kb = inputs.get_kb()
        self.data = {index: dict() for index in self.kb}

    def process(self, batch_size=100, n_jobs=2, partial_output_path="entailer.tmp.tsv", verbose=True):
        tasks = []
        for index in self.kb:
            premise = self.kb[index].subject
            hypothesis = self.kb[index].property
            tasks.append({
                "index": index,
                "premise": premise,
                "hypothesis": hypothesis
            })
        queue_in = mp.JoinableQueue()
        queue_out = mp.Queue()
        jobs = [Worker(queue_in, queue_out) for _ in range(n_jobs)]
        for job in jobs:
            job.start()
        remaining = 0
        for start in range(0, len(tasks), batch_size):
            remaining += 1
            queue_in.put(Task(tasks[start:start+batch_size]))
        for job in jobs:
            queue_in.put(None)
        if verbose:
            bar = ProgressBar(remaining)
            bar.start()
        if partial_output_path is not None:
            open(partial_output_path, "w").close()
        while remaining > 0:
            try:
                out = queue_out.get()
                remaining -= 1
                if verbose:
                    bar.increment()
                if partial_output_path is None:
                    for row in out:
                        self.data[row["index"]] = {
                            "premise": row["premise"],
                            "hypothesis": row["hypothesis"],
                            "entailment": row["entailment"],
                            "contradiction": row["contradiction"],
                            "neutral": row["neutral"],
                        }
                else:
                    with open(partial_output_path, "a") as file:
                        for row in out:
                            file.write("{i}\t{p}\t{h}\t{e}\t{c}\t{n}\n".format(
                                i=row["index"],
                                p=row["premise"],
                                h=row["hypothesis"],
                                e=row["entailment"],
                                c=row["contradiction"],
                                n=row["neutral"]
                            ))
            except queue.Empty:
                break
        if verbose:
            bar.stop()
        if partial_output_path is not None:
            with codecs.open(partial_output_path, "r", "utf8") as file:
                for line in file.readlines():
                    i, p, h, e, c, n = line.strip().split("\t")
                    self.data[int(i)] = {
                        "premise": p,
                        "hypothesis": h,
                        "entailment": float(e),
                        "contradiction": float(c),
                        "neutral": float(n),
                    }

    def save(self, path):
        with codecs.open(path, "w", "utf8") as file:
            file.write("index\tpremise\thypothesis\tentailment\tcontradiction\tneutral\n")
            for index in self.data:
                file.write("{i}\t{p}\t{h}\t{e}\t{c}\t{n}\n".format(
                    i=index,
                    p=self.data[index]["premise"],
                    h=self.data[index]["hypothesis"],
                    e=self.data[index]["entailment"],
                    c=self.data[index]["contradiction"],
                    n=self.data[index]["neutral"]
                ))

    def load(self, path):
        with codecs.open(path, "r", "utf8") as file:
            lines = file.readlines()
        self.data = dict()
        for line in lines[1:]:
            index, p, h, e, c, n = line.strip().split("\t")
            self.data[int(index)] = {
                "premise": p,
                "hypothesis": h,
                "entailment": float(e),
                "contradiction": float(c),
                "neutral": float(n),
            }
