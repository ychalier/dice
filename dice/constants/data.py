import os

class Data:

    folder = "data/"
    # attention_model = os.path.join(folder, "attention.tar.gz")
    attention_model = os.path.join(folder, "predictor")
    word2vec_model = os.path.join(folder, "word2vec.bin")
    word2vec_model_mmap = os.path.join(folder, "word2vec.model")
    quasimodo_kb = os.path.join(folder, "quasimodo.tsv")
    conceptnet_kb = os.path.join(folder, "conceptnet-kb.tsv")
    conceptnet_taxonomy = os.path.join(folder, "conceptnet-taxonomy.json")
    webisalod = os.path.join(folder, "webisavec.json")
    english_frequencies = os.path.join(folder, "english-frequencies.txt")
    sense_map_20_mono = os.path.join(folder, "sensemap/2.0to2.1.noun.mono")
    sense_map_20_poly = os.path.join(folder, "sensemap/2.0to2.1.noun.poly")
    sense_map_21_mono = os.path.join(folder, "sensemap/2.1to3.0.noun.mono")
    sense_map_21_poly = os.path.join(folder, "sensemap/2.1to3.0.noun.poly")
    tuple_kb = os.path.join(folder, "tuple-kb.tsv")
    wordnet_domains = os.path.join(folder, "wn-domains.tsv")
