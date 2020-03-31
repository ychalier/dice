# DICE: Joint-Reasoning for Multi-Faceted Commonsense Knowledge

## Setup

Install [Anaconda](https://www.anaconda.com/distribution/#download-section). Create a new environment using Python v3.6:

    conda create -n dice python=3.6

Then install the dependencies.

    source activate dice
    pip install -r requirements.txt

Now install the [Gurobi solver](http://www.gurobi.com/index). Follow the instructions from the [documentation](http://www.gurobi.com/documentation/7.0/quickstart_linux/software_installation_guid.html) to install it and retrieve a license. Here is an example of the `~/.bashrc` configuration:

    export GUROBI_HOME="${HOME}/gurobi811/linux64"
    export PATH="${PATH}:${GUROBI_HOME}/bin"
    export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
    export GRB_LICENSE_FILE="${HOME}/gurobi.lic.${HOSTNAME}"

Now download the required external resources and put them in a subfolder `data/`. Paths must match those written in the `dice.constants.Data` class. Here is an overview of them:

Resource | Path | Required | Source
--- | --- | --- | ---
Decomposable attention model | attention.tar.gz | yes | [AllenAI](https://github.com/allenai/allennlp/blob/master/MODELS.md) pre-trained model for [Textual Entailment](https://allennlp.s3.amazonaws.com/models/decomposable-attention-elmo-2018.02.19.tar.gz), based on [Parikh et al, 2017](https://www.semanticscholar.org/paper/A-Decomposable-Attention-Model-for-Natural-Languag-Parikh-T%C3%A4ckstr%C3%B6m/07a9478e87a8304fc3267fa16e83e9f3bbd98b27)
Word2vec model | word2vec.bin | only to generate the MMAP model | [GoogleNews pre-trained model](https://code.google.com/archive/p/word2vec/)
Word2vec model (Mapped Memory) | word2vec.model | yes | manually generated
Quasimodo KB | quasimodo.tsv | only for Quasimodo KB builder | Full [Quasimodo](https://www.dropbox.com/sh/r1os5uoo6v2xiac/AADinRFpUYSg1kQLm63pdMnOa?dl=0) statements
ConceptNet KB | conceptnet-kb.tsv | only for ConceptNet KB builder | [Commonsense Knowledge Representation resources](https://ttic.uchicago.edu/~kgimpel/commonsense.html) for [Li et al. (2016)](https://ttic.uchicago.edu/~kgimpel/papers/li+etal.acl16.pdf), top 300k ConceptNet statements
Tuple-KB | tuple-kb.tsv | only for TupleKb KB builder | [Aristo Tuple KB v5 (March 2017)](https://s3-us-west-2.amazonaws.com/ai2-website/data/artisto-tuple-kb/aristo-tuple-kb-v5-mar2017.zip)
English word frequencies | english-frequencies.txt | only for disambiguation into WordNet senses | [Invoke IT Word Frequency Lists](https://invokeit.wordpress.com/frequency-word-lists/) for English, 2012
ConcetpNet taxonomy | conceptnet-taxonomy.json | only for ConceptNet taxonomy builder | manually gathered
WebIsALOD | webisalod.json | only for WebIsALOD taxonomy builder | manually gathered

The manually generated/gathered files can be retrieved using the `gather.py` script.

    python gather.py

An archive containing everything needed is available for download [here](https://www.dropbox.com/s/zry48lf4k7rw7mo/data.tar.gz?dl=0) (2.5 GB) .

## Usage

Basic usage has the following form:

    python dice.py [FLAGS] <MODULE> [ARGUMENTS]

Use the `--help` flag for a detailed list of available modules and how to use them.

A common scenario starts with the formatting of a knowledge base through one of the kb builder modules (currently, `conceptnet_kb`, `tuple_kb` and `quasimodo_kb`), and then run the full `pipeline` on it.
