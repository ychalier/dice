import multiprocessing as mp
import os
from tqdm import tqdm

from dice import Pipeline
from dice import Inputs
from dice.process import BulkPipelineTask
from dice.process import BulkPipelineWorker
from dice.reason import Assignment
from dice.misc import notify

class BulkPipeline:

    def __init__(self, inputs_folder, partition, **parameters):
        self.inputs_folder = inputs_folder
        self.partition = partition
        self.parameters = parameters

    def pre_process(self):
        Pipeline(self.inputs_folder, self.parameters).process(list(range(1, 8)))

    def process(self, temp_folder, n_jobs=2, verbose=False, do_notify=False):
        inputs = Inputs(self.inputs_folder)
        inputs.load_kb()
        inputs.load_taxonomy()
        inputs.load_similarity_matrix()
        inputs.load_detective()
        queue_in = mp.JoinableQueue()
        queue_out = mp.Queue()
        jobs = [
            BulkPipelineWorker(inputs, queue_in, queue_out, False)
            for _ in range(n_jobs)
        ]
        for job in jobs:
            job.start()
        remaining = 0
        for i, part in enumerate(self.partition):
            remaining += 1
            queue_in.put(BulkPipelineTask(
                os.path.join(temp_folder, str(i)),
                self.parameters,
                part
            ))
        for job in jobs:
            queue_in.put(None)
        bar = tqdm(total=remaining, disable=not verbose)
        while remaining > 0:
            out = queue_out.get()
            remaining -= 1
            bar.update(1)
        bar.close()
        if do_notify:
            notify("Finished Processing", str(temp_folder))
