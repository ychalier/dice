from dice.reason import Assignment
from dice import Inputs
import tqdm
import os

class BulkGatherer:

    BUFFER_FILE = "assignment.tmp.tsv"

    def __init__(self, folder):
        self.folder = folder

    def gather(self, verbose=True):
        os.system("rm -f " + BulkGatherer.BUFFER_FILE)
        for i, part in tqdm.tqdm(list(enumerate(os.scandir(self.folder))), disable=not verbose):
            if i == 0:
                os.system("head -n 1 {path} >> {out}".format(
                    path=os.path.join(part.path, Inputs.ASSIGNMENT_PATH),
                    out=BulkGatherer.BUFFER_FILE
            ))
            os.system("tail -n +2 {path} >> {out}".format(
                path=os.path.join(part.path, Inputs.ASSIGNMENT_PATH),
                out=BulkGatherer.BUFFER_FILE
            ))
        assignment = Assignment([])
        assignment.load(BulkGatherer.BUFFER_FILE)
        os.system("rm -f " + BulkGatherer.BUFFER_FILE)
        return assignment
