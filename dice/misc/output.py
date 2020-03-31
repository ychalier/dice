import os

class Output:
    
    """
    Basic utility to export data to a dedicated folder.
    """
    
    def __init__(self, folder):
        self._folder = folder
        if not os.path.isdir(folder):
            os.makedirs(folder)
            
    def path(self, filename):
        return os.path.join(self._folder, filename)