import pandas as pd
import os

METHOD_AVERAGE = 0
METHOD_MOST_FREQUENT = 1

def evaluate_batch(filename, method=0):
    df = pd.read_csv(os.path.join("data/annotation/answer/", filename))
    df = df.where(df["Answer.pref.-1"] == False)\
           .dropna(how="all")\
           .rename(columns={
        "Input.dimension": "dimension",
        "Answer.pref.1": "gold",
        "Input.true": "prediction",
    })[["HITId", "dimension", "gold", "prediction"]]\
        .groupby(["HITId", "dimension"])\
        .mean()
    ppref = list()
    for index, row in df.iterrows():
        if method == 0:
            ppref.append(1 - abs(row["gold"] - row["prediction"]))
        elif method == 1:
            if row["gold"] > .5:
                ppref.append(row["prediction"])
            elif row["gold"] == .5:
                ppref.append(1)
            else:
                ppref.append(1 - row["prediction"])
    df["ppref"] = ppref
    df_grouped = df.groupby("dimension").mean()[["ppref"]]
    return {
        "Plausible": df_grouped.loc["Plausible"]["ppref"],
        "Typical": df_grouped.loc["Typical"]["ppref"],
        "Remarkable": df_grouped.loc["Remarkable"]["ppref"],
        "Salient": df_grouped.loc["Salient"]["ppref"],
        "Overall": df.mean()["ppref"]
    }

def evaluate(method):
    df = pd.DataFrame({
        "ConceptNet": evaluate_batch("Batch_3734867_batch_results.csv", method),
        "Quasimodo": evaluate_batch("Batch_3734869_batch_results.csv", method),
        # "TupleKb": evaluate_batch("Batch_3733961_batch_results.csv", method)
    }).reindex([
        "Plausible",
        "Typical",
        "Remarkable",
        "Salient",
        "Overall"
    ])
    return df

print(evaluate(METHOD_MOST_FREQUENT).to_latex(float_format="{:0.2f}".format))
print(evaluate(METHOD_AVERAGE).to_latex(float_format="{:0.2f}".format))
