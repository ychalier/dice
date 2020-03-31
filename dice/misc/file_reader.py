from dice.misc import ProgressBar

class FileReader:

    """
    Basic utility to read a file line by line and apply a funtion to each line.
    """

    def __init__(self, filename):
        self.filename = filename
        self.n_lines = 0
        with open(filename) as file:
            for i, line in enumerate(file):
                pass
        self.n_lines = i + 1
        self.index = 0

    def read(self, callback, skip_first=True, eof="", progress=True,
             format=False):
        first = True
        if progress:
            bar = ProgressBar(self.n_lines)
            bar.start()
        with open(self.filename) as file:
            while True:
                self.index += 1
                if progress:
                    bar.increment()
                line = file.readline().strip()
                if line == "":
                    break
                if first:
                    first = False
                    continue
                if format:
                    callback(line.strip().split("\t"), self.index, self.n_lines)
                else:
                    callback(line, self.index, self.n_lines)
        if progress:
            bar.stop()
