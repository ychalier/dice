from dice.evidence.cues import CueInterface
import tqdm

class JointCue(CueInterface):

    name = "joint"

    def gather(self, inputs, verbose=True, **args):
        kb = inputs.get_kb()
        probability = inputs.get_probability()
        for index in tqdm.tqdm(kb, disable=not verbose):
            self[index] = probability.joint(
                kb[index].subject,
                kb[index].property
            )
