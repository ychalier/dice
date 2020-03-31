import matplotlib.pyplot as plt
from dice.taxonomy import Taxonomy
from dice.constants import Dimensions

class EvidenceDrawer:

    def __init__(self, path, x, title, kb, taxonomy):
        self.path = path
        self.x = x
        self.title = title
        self.kb = kb
        self.taxonomy = taxonomy

    def percentile(self, nth):
        return sorted(self.x.values())[int(nth * len(self.x))]

    def top(self):
        nodes = self.taxonomy.relation._imap
        def custom_label(u):
            scores = sorted(
                [(fact, self.x[fact]) for fact in nodes.get(u, [])],
                key=lambda x: -x[1]
            )
            if len(scores) > 0:
                return u + "\n" + "\n".join([
                    self.kb[fact[0]].property
                    for fact in scores[:3]
                ])
            else:
                return u
        Taxonomy.draw(
            self.taxonomy,
            self.path + "-top.svg",
            custom_label=custom_label
        )

    def distrib(self):
        fig = plt.figure(figsize=(6, 6))
        fig.subplots_adjust(bottom=0.2)
        plt.hist(self.x.values(), density=True, bins=20)
        plt.title(self.title)
        plt.ylabel("Density")
        plt.xlabel("Cue\n\n"
            + "95th percentile: {}".format(self.percentile(.95))
            + "\n"
            + "99th percentile: {}".format(self.percentile(.99))
        )
        plt.savefig(self.path + "-distrib.png")
        plt.close()
