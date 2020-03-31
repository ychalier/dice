from dice.evidence.cues import *
from dice.constants import Dimensions
from dice.constants import Parameters

class EvidenceWrapper:

    def __init__(self, index, cues):
        self.index = index
        self.cues = {cue.name: cue.get(index, 0.) for cue in cues}
        self.plausible = self._plausible()
        self.typical = self._typical()
        self.remarkable = self._remarkable()
        self.salient = self._salient()

    def _plausible(self):
        return sum([Parameters.COEF_PLAUSIBLE_INTERCEPT,
            Parameters.COEF_PLAUSIBLE_JOINT * self.cues["joint"],
            Parameters.COEF_PLAUSIBLE_NECESSITY * self.cues["necessity"],
            Parameters.COEF_PLAUSIBLE_SUFFICIENCY * self.cues["sufficiency"],
            Parameters.COEF_PLAUSIBLE_IMPLICATION * self.cues["implication"],
            Parameters.COEF_PLAUSIBLE_CONTRADICTION * self.cues["contradiction"],
            Parameters.COEF_PLAUSIBLE_ENTAILMENT * self.cues["entailment"],
            Parameters.COEF_PLAUSIBLE_ENTROPY * self.cues["entropy"],
        ])

    def _typical(self):
        return sum([Parameters.COEF_TYPICAL_INTERCEPT,
            Parameters.COEF_TYPICAL_JOINT * self.cues["joint"],
            Parameters.COEF_TYPICAL_NECESSITY * self.cues["necessity"],
            Parameters.COEF_TYPICAL_SUFFICIENCY * self.cues["sufficiency"],
            Parameters.COEF_TYPICAL_IMPLICATION * self.cues["implication"],
            Parameters.COEF_TYPICAL_CONTRADICTION * self.cues["contradiction"],
            Parameters.COEF_TYPICAL_ENTAILMENT * self.cues["entailment"],
            Parameters.COEF_TYPICAL_ENTROPY * self.cues["entropy"],
        ])

    def _remarkable(self):
        return sum([Parameters.COEF_REMARKABLE_INTERCEPT,
            Parameters.COEF_REMARKABLE_JOINT * self.cues["joint"],
            Parameters.COEF_REMARKABLE_NECESSITY * self.cues["necessity"],
            Parameters.COEF_REMARKABLE_SUFFICIENCY * self.cues["sufficiency"],
            Parameters.COEF_REMARKABLE_IMPLICATION * self.cues["implication"],
            Parameters.COEF_REMARKABLE_CONTRADICTION * self.cues["contradiction"],
            Parameters.COEF_REMARKABLE_ENTAILMENT * self.cues["entailment"],
            Parameters.COEF_REMARKABLE_ENTROPY * self.cues["entropy"],
        ])

    def _salient(self):
        return sum([Parameters.COEF_SALIENT_INTERCEPT,
            Parameters.COEF_SALIENT_JOINT * self.cues["joint"],
            Parameters.COEF_SALIENT_NECESSITY * self.cues["necessity"],
            Parameters.COEF_SALIENT_SUFFICIENCY * self.cues["sufficiency"],
            Parameters.COEF_SALIENT_IMPLICATION * self.cues["implication"],
            Parameters.COEF_SALIENT_CONTRADICTION * self.cues["contradiction"],
            Parameters.COEF_SALIENT_ENTAILMENT * self.cues["entailment"],
            Parameters.COEF_SALIENT_ENTROPY * self.cues["entropy"],
        ])

    def __getitem__(self, key):
        if key == Dimensions.PLAUSIBLE:
            return self.plausible
        elif key == Dimensions.TYPICAL:
            return self.typical
        elif key == Dimensions.REMARKABLE:
            return self.remarkable
        elif key == Dimensions.SALIENT:
            return self.salient
        raise ValueError("Wrong key '{}'".format(key))

    def __setitem__(self, key, value):
        if key == Dimensions.PLAUSIBLE:
            self.plausible = value
        elif key == Dimensions.TYPICAL:
            self.typical = value
        elif key == Dimensions.REMARKABLE:
            self.remarkable = value
        elif key == Dimensions.SALIENT:
            self.salient = value
        return self[key]
