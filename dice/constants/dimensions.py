class Dimensions:

    PLAUSIBLE = 0
    TYPICAL = 1
    REMARKABLE = 2
    SALIENT = 3

    def label(dimension, slug=False):
        string = {
            Dimensions.PLAUSIBLE: "Plausible",
            Dimensions.TYPICAL: "Typical",
            Dimensions.REMARKABLE: "Remarkable",
            Dimensions.SALIENT: "Salient",
        }.get(dimension, "Unknown dimension")
        if slug:
            return string.lower().replace(" ", "-")
        return string

    def from_letter(letter):
        if letter == "P":
            return Dimensions.PLAUSIBLE
        elif letter == "T":
            return Dimensions.TYPICAL
        elif letter == "R":
            return Dimensions.REMARKABLE
        elif letter == "S":
            return Dimensions.SALIENT
        raise ValueError("Incorrect letter '{}'".format(letter))

    def from_label(label):
        if label == "plausible":
            return Dimensions.PLAUSIBLE
        elif label == "typical":
            return Dimensions.TYPICAL
        elif label == "remarkable":
            return Dimensions.REMARKABLE
        elif label == "salient":
            return Dimensions.SALIENT
        raise ValueError("Incorrect dimension label '{}'".format(label))

    def iter():
        return iter([
            Dimensions.PLAUSIBLE,
            Dimensions.TYPICAL,
            Dimensions.REMARKABLE,
            Dimensions.SALIENT
        ])

    def iter_labels(slug=False):
        return iter([
            (d, Dimensions.label(d, slug=slug))
            for d in Dimensions.iter()
        ])
