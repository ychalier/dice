import time

class Report:

    """
    Basic utility to wrap info-level log messages.
    """

    pattern_value = "{}:\t{}"
    pattern_value_ratio = "{}:\t{} ({}%)"

    def __init__(self):
        self.lines = ["Report generated on {}"
                      .format(time.strftime('%a, %d %b %Y %H:%M:%S'))]

    def __repr__(self):
        return "\n".join(self.lines)

    def __str__(self):
        return "\n".join(self.lines)

    def add(self, value):
        self.lines.append(str(value))

    def add_value(self, text, value):
        self.lines.append(
                self.pattern_value.format(
                        text,
                        lengthify(value)))

    def add_value_ratio(self, text, value, total):
        self.lines.append(
                self.pattern_value_ratio.format(
                        text,
                        lengthify(value),
                        percent(lengthify(value), lengthify(total))))

    def merge(self, other):
        self.lines.append("")
        for line in other.lines[1:]:
            self.lines.append(line)

    def save(self, filename):
        with open(filename, "w") as file:
            file.write(str(self))

def percent(value, total=1):
    if total == 0:
        return float("NaN")
    return round(100 * float(value) / float(total), 2)

def lengthify(value):
    if type(value) == type(""):
        return value
    try:
        iter(value)
        return len(list(value))
    except TypeError:
        return value
    else:
        raise ValueError("Incorrect value {}".format(value))
