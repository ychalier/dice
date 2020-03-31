from dice.process import KbExtender
from dice.constants import Dimensions
from dice.constants import Parameters

import multiprocessing as mp
import traceback
import queue
import tqdm
import os


def slugify(text):
    import unidecode
    import re
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '-', text)


class BulkKbExtenderTask:

    def __init__(self, subject, ratio):
        self.subject = subject
        self.ratio = ratio

    def __call__(self, worker):
        import os
        slug = slugify(self.subject)
        if os.path.isdir(os.path.join(worker.folder, slug)):
            os.system("rm -rf " + os.path.join(worker.folder, slug))
        tracker = worker.kb_extender.extend(
            self.subject,
            os.path.join(worker.folder, slug),
            verbose=False
        )
        dummy_indices = [
            index for index in tracker
            if tracker[index].source == Parameters.DUMMY_INJECTER_SOURCE
        ]
        base_size = len([
            index for index in tracker
            if tracker[index].subject == self.subject
        ])
        dummy_indices.sort(key=lambda i: -tracker[i].attributes[Dimensions.PLAUSIBLE]["confidence"])
        dummy_indices = set(dummy_indices[:int(self.ratio * (base_size - len(dummy_indices)))])
        for index in list(tracker.keys()):
            if index not in dummy_indices:
                del tracker[index]
        tracker.save(os.path.join(worker.folder, slug, "tracker.tsv"))
        return None


class BulkKbExtenderWorker(mp.Process):

    def __init__(self, kb_extender, folder, q_in, q_out):
        mp.Process.__init__(self)
        self.kb_extender = kb_extender
        self.q_in = q_in
        self.q_out = q_out
        self.folder = folder

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


class BulkKbExtender:

    def __init__(self, reference_inputs):
        self.reference_inputs = reference_inputs

    def process(self, ratio=.25, verbose=True, n_jobs=40, **args):
        if n_jobs is None:
            n_jobs = max(1, mp.cpu_count() // 2)
        queue_in = mp.JoinableQueue()
        queue_out = mp.Queue()
        jobs = [
            BulkKbExtenderWorker(
                KbExtender(self.reference_inputs),
                self.reference_inputs.path("dummy"),
                queue_in,
                queue_out
            )
            for i in range(n_jobs)
        ]
        for job in jobs:
            job.start()
        subjects = set(map(lambda fact: fact.subject, self.reference_inputs.get_kb().values()))
        remaining = 0
        for subject in subjects:
            remaining += 1
            queue_in.put(BulkKbExtenderTask(subject, ratio))
        for job in jobs:
            queue_in.put(None)
        pbar = tqdm.tqdm(total=remaining, disable=not verbose)
        while remaining > 0:
            try:
                out = queue_out.get(timeout=60)
                pbar.update(1)
                remaining -= 1
            except queue.Empty:
                break
        pbar.close()
