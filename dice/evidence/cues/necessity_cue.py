from dice.evidence.cues import JointCue
import tqdm

class NecessityCue(JointCue):

    name = "necessity"

    def gather(self, inputs, verbose=True, joint_cue=None):
        if joint_cue is None:
            JointCue.gather(self, inputs, verbose=verbose)
        else:
            for key, value in joint_cue.items():
                self[key] = value
        kb = inputs.get_kb()
        probability = inputs.get_probability()
        for index in tqdm.tqdm(kb, disable=not verbose):
            marginal = probability.marginal("c", kb[index].subject)
            if marginal > 0:
                self[index] /= marginal
