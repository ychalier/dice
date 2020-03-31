from dice.evidence.cues import CueInterface
import tqdm

class ContradictionCue(CueInterface):

    name = "contradiction"

    def gather(self, inputs, verbose=True, **kwargs):
        for index in tqdm.tqdm(inputs.get_kb(), disable=not verbose):
            self[index] = inputs.get_entailer().data[index]["contradiction"]
