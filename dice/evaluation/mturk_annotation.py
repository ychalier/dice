import pandas as pd
from dice.constants import Dimensions

class MTurkAnnotation:

    def __init__(self, path_singles, *paths_pairs):
        self.paths_pairs = paths_pairs
        self.path_singles = path_singles
        self.group = 4

    def build(self):
        pairs_dfs = list()
        for path in self.paths_pairs:
            df = pd.read_csv(path)
            inputs = df[[
                "HITId",
                "Input.index_1",
                "Input.index_2",
                "Input.source_1",
                "Input.source_2",
                "Input.subject",
                "Input.property_1",
                "Input.property_2"
            ]].drop_duplicates().set_index("HITId")
            answers = df[[
                "HITId",
                "Answer.remarkable",
                "Answer.salient",
                "Answer.typical"
            ]].groupby("HITId").mean()
            pairs_dfs.append(answers.join(inputs).rename(columns={
                "Answer.typical": Dimensions.TYPICAL,
                "Answer.salient": Dimensions.SALIENT,
                "Answer.remarkable": Dimensions.REMARKABLE,
                "Input.index_1": "index_1",
                "Input.index_2": "index_2",
                "Input.source_1": "source_1",
                "Input.source_2": "source_2",
                "Input.subject": "subject",
                "Input.property_1": "property_1",
                "Input.property_2": "property_2",
            }))
        pairs_df = pd.concat(pairs_dfs)
        pis = list()
        if self.path_singles is not None:
            singles_dfs = list()
            df = pd.read_csv(self.path_singles)
            for i in range(self.group):
                inputs = df[[
                    "HITId",
                    "Input.index_" + str(i),
                    "Input.source_" + str(i)
                ]].drop_duplicates().set_index("HITId")
                answers = df[[
                    "HITId",
                    "Answer.plausible" + str(i)
                ]].groupby("HITId").mean()
                singles_dfs.append(answers.join(inputs).rename(columns={
                    "Input.index_" + str(i): "index",
                    "Input.source_" + str(i): "source",
                    "Answer.plausible" + str(i): Dimensions.PLAUSIBLE,
                }))
            single_df = pd.concat(singles_dfs).set_index(["index", "source"])
            for index, row in pairs_df.iterrows():
                pi_1 = float(single_df.loc[
                                row["index_1"],
                                row["source_1"]
                            ][Dimensions.PLAUSIBLE][0])
                pi_2 = float(single_df.loc[
                                row["index_2"],
                                row["source_2"]
                            ][Dimensions.PLAUSIBLE][0])
                pis.append(3 + .5 * (pi_2 - pi_1))
        else:
            for index, row in pairs_df.iterrows():
                pis.append(3)
        pairs_df.insert(0, Dimensions.PLAUSIBLE, pis, True)
        return pairs_df
