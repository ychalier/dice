from .progress_bar import ProgressBar
from .file_reader import FileReader
from .report import Report
from .module_wrapper import ModuleWrapper
from .output import Output
from .archive import Archive
from .table import Table
from .rank import Rank

def notify(subject, body):
    import subprocess
    import os
    address = os.environ["USER"] + "@mpi-inf.mpg.de"
    p1 = subprocess.Popen(["echo", body], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["mailx", "-s", subject, "-r", address, "-c", address, address], stdin=p1.stdout)
