"""Commensense Knowledge Reasoning Framework
Usage: python dice.py [FLAGS] <MODULE> [ARGUMENTS]

Flags:
    --help      display this message
    --version   display current program version
"""

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

import sys

from dice.modules import modules

def fail():
    print(__doc__.split("\n")[1]
        + "\nTry 'python dice.py --help' for more information.")
    exit()

if __name__ == "__main__":
    import os
    os.environ["OMP_NUM_THREADS"] = "12"
    os.environ["OPENBLAS_NUM_THREADS"] = "12"
    os.environ["MKL_NUM_THREADS"] = "12"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "12"
    os.environ["NUMEXPR_NUM_THREADS"] = "12"
    if "--help" in sys.argv:
        print(__doc__)
        print("Modules:\n    " + "\n    ".join(modules.keys()) + "\n")
        for module in modules.values():
            print(module.doc)
        exit()
    elif "--version" in sys.argv:
        print("Commensense Knowledge Reasoning Framework 1.0")
        exit()
    if len(sys.argv) < 2:
        fail()
    module = sys.argv[1]
    if module == "test":
        from tests import tests
        tests.main()
    elif module not in modules:
        fail()
    else:
        pipeline = modules[module]
        pipeline.main()
