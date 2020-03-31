from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


class Fact:

    """
    Represents a fact from the KB.
    """

    header = [
        "index",
        "subject",
        "property",
        "score",
        "sense",
        "modality",
        "text",
        "source",
    ]

    stemmer = PorterStemmer()
    stopwords = set(stopwords.words("english"))
    delimiter = " // "

    def __init__(self):
        self.index = -1
        self.subject = ""
        self.property = ""
        self.modality = ""
        self.score = 0.
        self.text = ""
        self.sense = ""
        self.source = ""

    def __repr__(self):
        return "fact#{index}: {subject}; {property}".format(
            index=self.index,
            subject=self.subject,
            property=self.property,
        )

    def __str__(self):
        return "\t".join(map(str, [
            self.index,
            self.subject,
            self.property,
            self.score,
            self.sense,
            self.modality,
            self.text,
            self.source,
        ]))

    def _add_modality(self, modality):
        current = self.modality.split(self.delimiter)
        if "" in current:
            current.remove("")
        self.modality = self.delimiter.join(current + [modality])

    def _add_sentence(self, sentence):
        current = self.text.split(self.delimiter)
        if "" in current:
            current.remove("")
        self.text = self.delimiter.join(current + [sentence])

    def parse(self, line):
        split = line.strip().split("\t")
        self.index = int(split[0])
        self.subject = split[1]
        self.property = split[2]
        self.score = float(split[3])
        self.sense = split[4]
        self.modality = split[5]
        self.text = split[6]
        self.source = split[7]

    def get_sentences(self):
        return self.text.split(" // ")

    def get_stemmed_property(self):
        return " ".join([
            self.stemmer.stem(token)
            for token in word_tokenize(self.property)
            if token not in self.stopwords
        ])
