from zipfile import ZipFile
import os

class Archive:

    def __init__(self, path, mode="r"):
        self.path = path
        ZipFile(path, mode).close()

    def write(self, file, text):
        with ZipFile(self.path, "a") as zip:
            with zip.open(file, "w") as file:
                file.write(text.encode("utf8"))

    def read(self, file):
        with ZipFile(self.path, "r") as zip:
            with zip.open(file, "r") as file:
                text = file.read().decode("utf8")
        return text
