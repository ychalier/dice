import tqdm
import json
import sys
sys.path.append("..")
from dice.constants import Data
from gensim.models import KeyedVectors
import numpy as np

def embed(phrase):
    if phrase in known_embeddings:
        return known_embeddings[phrase]
    dummy = np.zeros((300,))
    embed = np.zeros((300,))
    count = 0
    for word in phrase.split(" "):
        if word in model:
            count += 1
            embed += model[word]
    if count > 0:
        embed /= count
    norm = np.linalg.norm(embed)
    if norm > 0:
        embed /= np.linalg.norm(embed)
    known_embeddings[phrase] = embed
    return embed

def sim(phrase_a, phrase_b):
    embed_a = embed(phrase_a)
    embed_b = embed(phrase_b)
    return .5 * ((embed_a @ embed_b.T) + 1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python webisalod_word2vec.py <output-path>")
        exit()
    output_path = sys.argv[1]
    known_embeddings = dict()
    with open("../" + Data.webisalod) as file:
        hypernyms = json.load(file)
    model = KeyedVectors.load("../" + Data.word2vec_model_mmap, mmap="r")
    new_hypernyms = dict()
    for i, subject in tqdm.tqdm(list(enumerate(hypernyms))):
        new_hypernyms[subject] = dict()
        for parent in hypernyms[subject]:
            webisalod = hypernyms[subject][parent]
            word2vec = sim(subject, parent)
            if webisalod == 0. or word2vec == 0.:
                mixed = 0.
            else:
                mixed = 3. / (1. / webisalod + 2. / word2vec)
            new_hypernyms[subject][parent] = {
                "webisalod": webisalod,
                "word2vec": word2vec,
                "mixed": mixed,
            }
    with open(output_path, "w") as file:
        json.dump(new_hypernyms, file)
