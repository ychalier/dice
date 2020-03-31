import matplotlib.pyplot as plt

class CueInterface(dict):

    name = "cue"

    def gather(self, inputs):
        raise NotImplementedError
