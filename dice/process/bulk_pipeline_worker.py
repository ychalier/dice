import multiprocessing as mp
import gurobipy
import traceback

class BulkPipelineWorker(mp.Process):

    def __init__(self, inputs, q_in, q_out, verbose):
        mp.Process.__init__(self)
        self.verbose = verbose
        self.inputs = inputs
        self.q_in = q_in
        self.q_out = q_out

    def run(self):
        while True:
            task = self.q_in.get()
            if task is None:
                self.q_in.task_done()
                break
            out = None
            try:
                out = task(self)
            # except gurobipy.GurobiError:
            #     pass
            except Exception as e:
                print("\nError in Worker {worker} | \n{error}".format(
                    worker=self.name,
                    error=e
                ))
                print(traceback.format_exc())
            finally:
                self.q_out.put(out)
                self.q_in.task_done()
