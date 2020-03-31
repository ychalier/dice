from dice.evidence.cues import JointCue
import tqdm

class SufficiencyCue(JointCue):

    name = "sufficiency"

    def gather(self, inputs, verbose=True, joint_cue=None):
        if joint_cue is None:
            JointCue.gather(self, inputs, verbose=verbose)
        else:
            for key, value in joint_cue.items():
                self[key] = value
        kb = inputs.get_kb()
        probability = inputs.get_probability()
        for index in tqdm.tqdm(kb, disable=not verbose):
            marginal = probability.marginal("p", kb[index].property)
            if marginal > 0:
                self[index] /= marginal
