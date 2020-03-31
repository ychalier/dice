from dice.constants import Dimensions
import language_check
import random
import tqdm
import re

class DialogueGenerator:

    REMARKABLE_SCRIPT = """
{{1_remarkable_up}} {{2_remarkable_down}} {{bind_1_2}} {{be_are}}
Alice: What's something very peculiar about {{s_1}}s?
Bot: They {{p_1}}.
Alice: Yeah true. And they {{p_2}}.
Bot: This is not really surprising.
    """

    SALIENT_SCRIPT = """
{{1_salient_up}} {{2_salient_up}} {{bind_1_2}} {{be_are}}
Alice: Can you tell me something about {{s_1}}s?
Bot: They {{p_1}}.
Alice: Yeah. Something else?
Bot: They {{p_2}}.
    """

    PLAUSIBLE_SCRIPT = """
{{1_plausible_down}} {{2_plausible_up}} {{bind_1_2}} {{be_was}}
Alice: Yesterday I saw an {{s_1}} that {{p_1}}.
Bot: Well that is odd!
Alice: I also saw an {{s_2}} that {{p_2}}.
Bot: Yeah, that sounds more credible.
    """

    TYPICAL_SCRIPT = """
{{1_typical_down}} {{2_typical_up}} {{bind_1_2}} {{be_was}}
Alice: Yesterday I saw an {{s_1}} that {{p_1}}.
Bot: That is rare!
Alice: I also saw an {{s_2}} that {{p_2}}.
Bot: Well yeah this is common.
    """

    def __init__(self, tracker, random_seed=None):
        self.tracker = tracker
        if random_seed is None:
            random_seed = random.randint(1, 2**31 - 1)
        self.seed = random_seed
        random.seed(random_seed)
        self.tool = language_check.LanguageTool("en-US")

    def generate(self, script, remote_subject_filter=None):
        declaration_regex = re.compile("{{(\d+)_(salient|typical|plausible|remarkable|random|score)_(up|down)}}")
        placeholder_regex = re.compile("{{(s|p)_(\d+)}}")
        bindings_regex = re.compile("{{bind_(\d+)_(\d+)}}")
        bes_regex = re.compile("{{be_(\w+)}}")
        bindings = bindings_regex.findall(script)
        be_rep = list(bes_regex.findall(script))
        if len(be_rep) > 0:
            be_rep = be_rep[0]
        else:
            be_rep = "be"

        while True:

            facts = dict()
            selected = set()

            retry = False

            for index, dimension, direction in declaration_regex.findall(script):

                # Checking if the fact is already bound to another one
                subject_filter = None
                for pair in bindings:
                    if index not in set(pair):
                        continue
                    index_a, index_b = pair
                    if index == index_a and index_b in facts:
                        subject_filter = facts[index_b].subject
                    elif index == index_b and index_a in facts:
                        subject_filter = facts[index_a].subject
                if remote_subject_filter is not None:
                    subject_filter = remote_subject_filter

                # Getting the list of new facts
                source = [
                    fact for fact in self.tracker.values() if fact.index not in selected and " " not in fact.subject]

                # Applying filter if necessary
                if subject_filter is not None:
                    source = [fact for fact in source if fact.subject == subject_filter]

                # Re-do the sampling if the current one would not have enough facts
                if len(source) == 0:
                    retry = True
                    break

                # Sorting facts according to the correct dimension
                if dimension == "random":
                    random.shuffle(source)
                    ranked = source[:]
                elif dimension == "score":
                    ranked = sorted(source, key=lambda fact: fact.score)
                else:
                    ranked = sorted(
                        source,
                        key=lambda
                            fact:
                            fact.attributes[Dimensions.from_label(dimension)]["confidence"]
                    )

                # Narrowing down selection space
                slice = []
                if direction == "up":
                    slice = ranked[int(.9*len(ranked)):]
                elif direction == "down":
                    slice = ranked[:int(.1*len(ranked))]
                if len(slice) == 0:
                    if direction == "up":
                        slice = ranked[-1:]
                    elif direction == "down":
                        slice = ranked[:1]

                # Choosing and selecting fact
                fact = random.choice(slice)
                selected.add(fact.index)
                facts[index] = fact

            # Reaching this points ensures that all facts have been correctly
            # sampled.
            if not retry:
                break

        out = declaration_regex.sub("", script)
        out = bindings_regex.sub("", out)
        out = bes_regex.sub("", out)
        def replacer(match):
            field, index = match.group(1), match.group(2)
            if field == "s":
                return facts[index].subject
            return facts[index].property.replace("be ", be_rep + " ")
        text = placeholder_regex.sub(replacer, out).strip()
        corrected = ""
        for sentence in text.split("\n"):
            matches = self.tool.check(sentence)
            corrected_sentence = language_check.correct(sentence, matches)
            corrected += corrected_sentence.strip() + "\n"
        return {
            "text": text,
            "html": re.sub("\n", "<br>", corrected),
            "samples": facts,
            "seed": self.seed
        }

    def generate_batch(self, batch_size, verbose=True, baseline="random"):
        import pandas as pd
        batch = list()
        scripts = (
            ("Remarkable", self.REMARKABLE_SCRIPT),
            ("Salient", self.SALIENT_SCRIPT),
            ("Plausible", self.PLAUSIBLE_SCRIPT),
            ("Typical", self.TYPICAL_SCRIPT),
        )
        pbar = tqdm.tqdm(total=len(scripts)*batch_size, disable=not verbose)
        pattern = re.compile("(salient|typical|remarkable|plausible)")
        for i in range(batch_size):
            for j, (name, script) in enumerate(scripts):
                dialogue_true = self.generate(script)
                dialogue_random = self.generate(pattern.sub("score", script), list(dialogue_true["samples"].values())[0].subject)
                dialogue_score = self.generate(pattern.sub("random", script), list(dialogue_true["samples"].values())[0].subject)
                indices = [0, 1]
                random.shuffle(indices)
                if baseline == "random":
                    dialogues = [dialogue_true, dialogue_random]
                else:
                    dialogues = [dialogue_true, dialogue_score]
                row = {
                    "id": 4 * i + j,
                    "true": indices[0],
                    "baseline": indices[1],
                }
                for j in indices:
                    row["dialogue_" + str(j)] = dialogues[j]["html"]
                row["dimension"] = name
                batch.append(row)
                pbar.update(1)
        pbar.close()
        return pd.DataFrame(batch).set_index("id")
