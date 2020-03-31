from dice.evidence.cues import CueInterface
import tqdm

class EntailmentCue(CueInterface):

    name = "entailment"

    def gather(self, inputs, verbose=True, **args):
        for index in tqdm.tqdm(inputs.get_kb(), disable=not verbose):
            self[index] = inputs.get_entailer().data[index]["entailment"]
