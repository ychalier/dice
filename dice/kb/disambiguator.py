from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

from dice.kb import KnowledgeBase
from dice.misc import ProgressBar
from dice.constants import Data

def avg(iterable):
    return float(sum(iterable)) / len(list(iterable))

def normalize(counts):
    total = sum(counts.values())
    if total == 0:
        total = 1
    return { key: float(value)/total for key, value in counts.items() }

class Disambiguator:

    def __init__(self, kb_path, alpha=.6):
        self.kb = KnowledgeBase()
        self.kb.load(kb_path)
        self.kb_path = kb_path
        self._alpha = alpha
        self._stop_words = set(stopwords.words("english"))
        self._tokenizer = RegexpTokenizer(r"\w+")
        self._frequencies = dict()
        with open(Data.english_frequencies) as file:
            while True:
                line = file.readline()
                if line == "":
                    break
                word, count = line.strip().split(" ")
                self._frequencies[word] = int(count)

    def _extract_headword(self, phrase):
        return phrase.split(" ")[-1]  # TODO: better headword extraction

    def _gather_candidates(self, word):
        synsets = wn.synsets(word, pos=wn.NOUN)
        if len(synsets) == 0:
            synsets = wn.synsets("_".join(word.split(" ")), pos=wn.NOUN)
        if len(synsets) == 0:
            synsets = wn.synsets(self._extract_headword(word), pos=wn.NOUN)
        return synsets

    def _compute_prior(self, synsets):
        lemmas = { s: s.lemmas() for s in synsets }
        prior = { s: sum([l.count() for l in lemmas[s]]) for s in synsets }
        if sum(prior.values()) == 0:
            prior = { s: avg([self._frequencies.setdefault(l.name(), 0)
                            for l in lemmas[s]]) for s in synsets}
        if sum(prior.values()) == 0:
            prior =  { s: len(lemmas[s]) for s in synsets }
        return normalize(prior)

    def _tokenize(self, sentence):
        tokens = set()
        for word in self._tokenizer.tokenize(sentence):
            if word not in self._stop_words:
                tokens.add(word.lower())
        return tokens

    def _compute_context(self, sentences, synsets):
        ref = self._tokenize(" ".join(sentences))
        target = { s: self._tokenize(s.definition() + " ".join(s.examples()))
                    for s in synsets }
        context = { s: len(ref.intersection(target[s])) for s in synsets }
        return normalize(context)

    def _compute_score(self, prior, context):
        return self._alpha * prior + (1 - self._alpha) * context

    def disambiguate(self, fact):
        synsets = self._gather_candidates(fact.subject)
        if len(synsets) == 0:
            return None, None, None
        prior = self._compute_prior(synsets)
        context = self._compute_context(fact.get_sentences(), synsets)
        scores = {s: self._compute_score(prior[s], context[s]) for s in synsets}
        senses = sorted(scores.items(), key=lambda item: -item[1])
        return senses[0][0], prior[senses[0][0]], context[senses[0][0]]

    def process(self):
        blacklist = set()
        bar = ProgressBar(len(self.kb))
        print("Disambiguating...")
        bar.start()
        for fact in self.kb.values():
            if fact.subject in blacklist:
                continue
            sense, prior, context = self.disambiguate(fact)
            if sense is not None:
                fact.sense = sense.name()
            else:
                blacklist.add(fact.subject)
            bar.increment()
        bar.stop()
        self.kb.save(self.kb_path)
