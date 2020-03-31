import sys

class ModuleWrapper:

    """
    Interfaces between the menu and the procedures requiring module scripts.
    """

    def __init__(self, fun, argc_min=None, argc_max=None):
        self._fun = fun
        self._argc_min = argc_min
        self._argc_max = argc_max
        self.doc = fun.__doc__

    def _valid_argc(self, argc):
        if self._argc_min is not None and argc < self._argc_min:
            return False
        if self._argc_max is not None and argc > self._argc_max:
            return False
        return True

    def main(self):
        argv = sys.argv[2:]
        if self._valid_argc(len(argv)):
            self._fun(argv)
        else:
            print(self._fun.__doc__)
            exit()
