from dice.evidence.cues import CueInterface
import tqdm

class ImplicationCue(CueInterface):

    name = "implication"

    def gather(self, inputs, verbose=True, **args):
        kb = inputs.get_kb()
        probability = inputs.get_probability()
        for index in tqdm.tqdm(kb, disable=not verbose):
            c = kb[index].subject
            p = kb[index].property
            self[index] = 1\
                - probability.marginal("c", c)\
                + probability.joint(c, p)
