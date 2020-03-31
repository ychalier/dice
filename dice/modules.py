from dice.misc import ModuleWrapper

################################################################################
# PIPELINE
################################################################################

def pipeline(argv):
    """pipeline
    arguments:  <inputs-folder> [parameter=value]*

    options:    NAME                            DEFAULT VALUE
                log                             False
                verbose                         False
                notify                          False
                logger_path                     log
                kb_path                         data/kb.tsv
                entailer_batch_size             100
                entailer_n_jobs                 2
                steps                           1-8

    parameters:
                SIMILARITY_THRESHOLD = .75
                REMARKABLE_ALPHA = 0.2861481307916379
                TYPICAL_ALPHA = 0.9982891056446265
                TYPICAL_BETA = 0.0009590134436654157
                PLAUSIBLE_ALPHA = 0.3420266845860523
                PLAUSIBLE_BETA = 0.6786119833435241
                EVIDENCE_OFFSET = 1.3396791371188632
                ASSIGNMENT_METHOD = 1
                TAXONOMY_BUILDER = "webisalod"
                TAXONOMY_BUILDER_LOWS_THRESHOLD = 10
                TAXONOMY_BUILDER_EDGE_THRESHOLD = .4
                FUSE_ALPHA = .8
                FUSE_THRESHOLD = .1
                RULE_EXISTENCE_WEIGHT = 10.
                RULE_NOT_PLAUSIBLE_IMPLIES_REMARKABLE_SIBLINGS_WEIGHT = 0.4136813802555934
                RULE_NOT_PLAUSIBLE_IMPLIES_REMARKABLE_WEIGHT = 0.8385061349318154
                RULE_PLAUSIBILITY_INFERENCE_WEIGHT = 0.8899064124827547
                RULE_PLAUSIBILITY_INHERITANCE_WEIGHT = 0.09630439631215232
                RULE_REMARKABILITY_INHERITANCE_WEIGHT = 0
                RULE_REMARKABILITY_SIBLINGS_WEIGHT = 0.01
                RULE_SALIENT_IMPLIES_PLAUSIBLE_WEIGHT = 0.10873639531265827
                RULE_TYPICAL_AND_REMARKABLE_IMPLY_SALIENT_WEIGHT = 0
                RULE_TYPICAL_IMPLIES_PLAUSIBLE_WEIGHT = 0.5446133523460819
                RULE_TYPICAL_PREVENTS_REMARKABLE_SIBLINGS_WEIGHT = 0.0331447944410993
                RULE_TYPICAL_PREVENTS_REMARKABLE_WEIGHT = 0.05332233624133091
                RULE_TYPICALITY_INFERENCE_WEIGHT = 0.42207454477107076
                RULE_TYPICALITY_INHERITANCE_WEIGHT = 0.5266373056914903
                RULE_SIMILARITY_WEIGHT = 0.9843530983393707
                DUMMY_INJECTER_THRESHOLD = 0.0002
                DUMMY_INJECTER_SOURCE = "DUMMY"

    taxonomy_builder: {conceptnet|webisalod|wordnet|merged}

    assignment method:
                0:  Maximum Satisfiability
                1:  Integer Linear Programming

    steps:
                1. Loading knowledge base
                2. Building taxonomy
                3. Embedding facts
                4. Computing similarity matrix
                5. Computing probability
                6. Computing entailment
                7. Computing evidence
                8. Assigning dimensions
    """
    from dice import Pipeline
    inputs_folder, *parameters = argv
    args = {p.split("=")[0]: p.split("=")[1] for p in parameters}
    pipeline = Pipeline(inputs_folder, args)
    steps = [i for i in range(1, 9)]
    if "steps" in args:
        steps = []
        for isolated_range in args["steps"].split(","):
            if "-" in isolated_range:
                start, stop = tuple(map(int, isolated_range.split("-")))
                steps += [i for i in range(start, stop+1)]
            else:
                steps.append(int(isolated_range))
    pipeline.process(steps)
    # pipeline.save()  # DOUBLE SAVING COSTLY FOR LARGE INPUT

def clone_inputs(argv):
    """clone_inputs
    arguments:  <inputs-folder> <clone-folder>
    """
    from dice import Inputs
    inputs_folder, clone_folder = argv
    Inputs(inputs_folder, load=True).clone(clone_folder).save()

def kb_extender(argv):
    """kb_extender
    arguments:  <inputs-folder> <subjects>+
    """
    from dice.process import KbExtender
    from dice import Inputs
    import os
    inputs_folder, *subjects = argv
    inputs = Inputs(inputs_folder)
    kb_extender = KbExtender(inputs)
    for subject in subjects:
        tracker = kb_extender.extend(subject, os.path.join(inputs_folder, "dummy", subject))
        tracker.save(os.path.join(inputs_folder, "dummy", subject, "tracker.tsv"))

def bulk_kb_extender(argv):
    """bulk_kb_extender
    arguments:  <inputs-folder> <ratio> <verbose> <n_jobs>
    """
    from dice.process import BulkKbExtender
    from dice import Inputs
    import os
    inputs_folder, ratio, verbose, n_jobs = argv
    inputs = Inputs(inputs_folder)
    bulk_kb_extender = BulkKbExtender(inputs)
    bulk_kb_extender.process(float(ratio), verbose=="True", int(n_jobs))

def bulk_pipeline(argv):
    """bulk_pipeline
    arguments:  <inputs-folder> <temporary-folder> <n-jobs> <partition-file> <verbose> <notify> [parameter=value]*
    parameters: see `pipeline`
    """
    from dice.process import BulkPipeline
    from dice.process import BulkPipelineTask
    inputs_folder, temp_folder, n_jobs, partition_file, verbose, notify, *parameters = argv
    # BulkPipelineTask.NEIGHBOR_THRESHOLD = int(neighborhood_threshold)
    # BulkPipelineTask.ABSOLUTE_THRESHOLD = int(absolute_threshold)
    args = {p.split("=")[0]: p.split("=")[1] for p in parameters}
    partition = list()
    with open(partition_file) as file:
        for line in file.readlines():
            partition.append(list(map(int, line.strip().split("\t"))))
    pipeline = BulkPipeline(inputs_folder, partition, **args)
    pipeline.process(temp_folder, int(n_jobs), verbose=="True", notify=="True")

def bulk_gatherer(argv):
    """bulk_gatherer
    arguments:  <inputs-folder> <bulk-folder>
    """
    from dice.process import BulkGatherer
    from dice import Inputs
    inputs_folder, bulk_folder = argv
    Inputs(inputs_folder).set_assignment(BulkGatherer(bulk_folder).gather())

def bulk_tuner(argv):
    """bulk_tuner
    arguments:  <annotation-file> <feature> <max-evals> <plan> <inputs-folder> <partition-file> <n-jobs> <trials-file>
    """
    from dice.process import BulkTuner
    annotation_file, feature, max_evals, plan, inputs_folders, partition_file, n_jobs, trials_file = argv
    tuner = BulkTuner(annotation_file, feature, inputs_folders, partition_file, n_jobs)
    print(tuner.optimize(plan, int(max_evals), trials_file))

def partitioner(argv):
    """partitioner
    arguments:  <inputs-folder> <save-path> <max-cluster-size> <max-neighborhood-size> <max-siblings> <n-jobs>
    """
    from dice.process import Partitioner
    from dice import Inputs
    inputs_folder, save_path, max_cluster_size, max_neighborhood_size, max_siblings, n_jobs = argv
    partitioner = Partitioner(Inputs(inputs_folder), int(max_cluster_size), int(max_neighborhood_size), int(max_siblings))
    partition = partitioner.process(int(n_jobs))
    partitioner.save(partition, save_path)

def bulk_process(argv):
    """bulk_process
    arguments:  <inputs-folder> <bulk-folder> <n-jobs> <partition-file> <tracker-path> <verbose> <notify>
    """
    from dice.process import BulkPipeline
    from dice.process import BulkPipelineTask
    from dice.process import BulkGatherer
    from dice import Inputs
    from dice.evaluation import Tracker
    from dice.misc import notify
    inputs_folder, bulk_folder, n_jobs, partition_file, tracker_path, verbose, do_notify = argv
    partition = list()
    with open(partition_file) as file:
        for line in file.readlines():
            partition.append(list(map(int, line.strip().split("\t"))))
    verbose = verbose == "True"
    pipeline = BulkPipeline(inputs_folder, partition, **{})
    pipeline.process(bulk_folder, int(n_jobs), verbose, False)
    if verbose:
        print("Gathering assignment...")
    inputs = Inputs(inputs_folder)
    inputs.set_assignment(BulkGatherer(bulk_folder).gather())
    if verbose:
        print("Gathering tracker...")
    tracker = Tracker()
    tracker.build(inputs)
    tracker.save(tracker_path)
    if do_notify == "True":
        notify("Bulk Process", """Finished processing for the following arguments:
        inputs folder: {inputs_folder}
        bulk folder: {bulk_folder}
        n jobs: {n_jobs}
        partition file: {partition_file}
        tracker path: {tracker_path}
        """.format(
            inputs_folder=inputs_folder,
            bulk_folder=bulk_folder,
            n_jobs=n_jobs,
            partition_file=partition_file,
            tracker_path=tracker_path
        ))

def prettify_tracker(argv):
    """prettify_tracker
    arguments:  <tracker-file> <output-path>
    """
    import pandas as pd
    tracker_file, output_path = argv
    df = pd.read_csv(tracker_file, delimiter="\t").set_index("index").rename(columns={
        "plausible_confidence": "plausible",
        "typical_confidence": "typical",
        "remarkable_confidence": "remarkable",
        "salient_confidence": "salient",
    })[[
        "subject",
        "property",
        "score",
        "plausible",
        "typical",
        "remarkable",
        "salient",
        "text"
    ]]
    n = df.shape[0]
    for column in ["plausible", "typical", "remarkable", "salient"]:
        df = df.sort_values(by=column)
        df[column] = [i / (n-1) for i in range(n)]
    df.sort_values(by="index").to_csv(output_path, index=False)

################################################################################
# KNOWLEDGE BASE
################################################################################

def kb_builder(argv):
    """kb_builder
    arguments:  <builder> <source> <seeds>* <save-path>
    builder:    {quasimodo|conceptnet|tuplekb}
    """
    builder, source, *seeds, save_path = argv
    if builder == "quasimodo":
        from dice.kb import QuasimodoKb
        kb = QuasimodoKb(source, *seeds)
    elif builder == "conceptnet":
        from dice.kb import ConceptNetKb
        kb = ConceptNetKb(source, *seeds)
    elif builder == "tuplekb":
        from dice.kb import TupleKb
        kb = TupleKb(source, *seeds)
    kb.build()
    kb.save(save_path)

def disambiguator(argv):
    """disambiguator
    Disambiguate the subjects of a KB file.
    arguments:  <kb-path>
    """
    from dice.kb import Disambiguator
    Disambiguator(argv[0]).process()

def kb_merge(argv):
    """kb_merge
    arguments:  <kb-file-a> <kb-file-b> <save-path>
    """
    from dice.kb import KnowledgeBase
    kb_file_a, kb_file_b, save_path = argv
    kb_merged = KnowledgeBase()
    new_index = 1
    for source in [kb_file_a, kb_file_b]:
        for fact in KnowledgeBase(source).values():
            fact.index = new_index
            kb_merged[new_index] = fact
            new_index += 1
    kb_merged.save(save_path)

################################################################################
# EVALUATION
################################################################################

def tracker(argv):
    """tracker
    arguments:  <inputs-folder> <save-path>
    """
    from dice import Inputs
    from dice.evaluation import Tracker
    inputs_folder, save_path = argv
    tracker = Tracker()
    tracker.build(Inputs(inputs_folder, load=True))
    tracker.save(save_path)

def pair_sampler(argv):
    """pair_sampler
    arguments:  <tracker-file> <amount> <save-path>
    """
    from dice.evaluation import Tracker, PairSampler
    tracker_file, amount, save_path = argv
    sampler = PairSampler(Tracker(tracker_file))
    sampler.process(save_path, int(amount))

def pair_evaluator(argv):
    """pair_evaluator
    arguments:  <annotation-file> <feature> <confidence> <tracker-file>+
    """
    from dice.evaluation import Tracker, PairEvaluator
    from dice.constants import Dimensions
    annotation_file, feature, confidence, *tracker_files = argv
    PairEvaluator.FEATURE = feature
    PairEvaluator.CONFIDENCE = float(confidence)
    evaluator = PairEvaluator(annotation_file, *[Tracker(f) for f in tracker_files])
    print(" " * 8 + "\t ppref\t size")
    for dimension, results in evaluator.evaluate(details=True).items():
        if dimension == -1:
            print(
                "Overall \t",
                round(1 - results["mae"], 2),
                "\t",
                results["n"]
            )
        else:
            print(
                Dimensions.label(dimension),
                "\t",
                round(1 - results["mae"], 2),
                "\t",
                results["n"]
        )

def bayesian_tuner(argv):
    """bayesian_tuner
    arguments:  <annotation-file> <feature> <max-evals> <plan> <inputs-folder>+
    """
    from dice.evaluation import BayesianTuner
    annotation_file, feature, max_evals, plan, *inputs_folders = argv
    tuner = BayesianTuner(annotation_file, feature, *inputs_folders)
    print(tuner.optimize(plan, int(max_evals)))

def mturk_annotation(argv):
    """mturk_annotation
    arguments:  <save-path> <singles-path> <pairs-paths>+
    """
    from dice.evaluation import MTurkAnnotation
    save_path, singles_path, *pairs_paths = argv
    df = MTurkAnnotation(singles_path, *pairs_paths).build()
    df.to_csv(save_path, index=False)

def dialogue_generator(argv):
    """dialogue_generator
    arguments:  <tracker-file> <script>
    """
    from dice.evaluation import Tracker
    from dice.evaluation import DialogueGenerator
    tracker_file, script = argv
    tracker = Tracker()
    tracker.load(tracker_file)
    generator = DialogueGenerator(tracker)
    if script == "typical":
        script = DialogueGenerator.TYPICAL_SCRIPT
    elif script == "plausible":
        script = DialogueGenerator.PLAUSIBLE_SCRIPT
    elif script == "salient":
        script = DialogueGenerator.SALIENT_SCRIPT
    elif script == "remarkable":
        script = DialogueGenerator.REMARKABLE_SCRIPT
    print(generator.generate(script)["corrected"])

def dialogue_generator_batch(argv):
    """dialogue_generator
    arguments:  <tracker-file> <batch-size> <output-path>
    """
    from dice.evaluation import Tracker
    from dice.evaluation import DialogueGenerator
    import pandas as pd
    tracker_file, batch_size, output_path = argv
    tracker = Tracker()
    tracker.load(tracker_file)
    generator = DialogueGenerator(tracker)
    df = generator.generate_batch(int(batch_size))
    df.to_csv(output_path)

def demo(argv):
    """demo
    arguments:  <inputs-folder> <partition-file> <max-facts-per-subjects> <clean-source> <save-folder>
    """
    inputs_folder, partition_file, maximum_facts_per_subject, clean_source, save_path = argv
    from dice import Inputs
    from dice.misc import Output
    from dice.constants import Dimensions
    from dice.reason import Variable
    from dice.evidence.cues import JointCue
    from dice.evidence.cues import NecessityCue
    from dice.evidence.cues import SufficiencyCue
    from dice.evidence.cues import ImplicationCue
    from dice.evidence.cues import EntailmentCue
    from dice.evidence.cues import ContradictionCue
    from dice.evidence.cues import EntropyCue
    from tqdm import tqdm
    import pandas as pd
    output = Output(save_path)
    inputs = Inputs(inputs_folder)
    print("Loading inputs...")
    kb = inputs.get_kb()
    taxonomy = inputs.get_taxonomy()
    detective = inputs.get_detective()
    assignment = inputs.get_assignment()
    similarity = inputs.get_similarity_matrix()
    data = list()
    selected_indices = set()
    subjects_representation = dict()
    print("Selecting indices...")
    for fact in tqdm(inputs.get_kb().values()):
        subjects_representation.setdefault(fact.subject, list())
        subjects_representation[fact.subject].append(fact.index)
    print("Thresholding number of facts per subject...")
    for subject, indices in tqdm(subjects_representation.items()):
        # if len(indices) > 20:
        selected_indices = selected_indices.union(indices[:int(maximum_facts_per_subject)])
    print("Gathering facts...")
    for fact in tqdm(inputs.get_kb().values()):
        if fact.index not in selected_indices:
            continue
        data.append({
            "index": fact.index,
            "source": clean_source,
            "subject": fact.subject,
            "property": fact.property,
            "score": fact.score,
            "evidence_plausible": detective[fact.index].plausible,
            "evidence_typical": detective[fact.index].typical,
            "evidence_remarkable": detective[fact.index].remarkable,
            "evidence_salient": detective[fact.index].salient,
            "cue_joint": detective.cues[JointCue][fact.index],
            "cue_necessity": detective.cues[NecessityCue][fact.index],
            "cue_sufficiency": detective.cues[SufficiencyCue][fact.index],
            "cue_implication": detective.cues[ImplicationCue][fact.index],
            "cue_entailment": detective.cues[EntailmentCue][fact.index],
            "cue_contradiction": detective.cues[ContradictionCue][fact.index],
            "cue_entropy": detective.cues[EntropyCue][fact.index],
            "plausible": assignment.confidence.get(Variable(fact.index, Dimensions.PLAUSIBLE), 0),
            "typical": assignment.confidence.get(Variable(fact.index, Dimensions.TYPICAL), 0),
            "remarkable": assignment.confidence.get(Variable(fact.index, Dimensions.REMARKABLE), 0),
            "salient": assignment.confidence.get(Variable(fact.index, Dimensions.SALIENT), 0),
            "plausible_percentile": assignment.confidence.get(Variable(fact.index, Dimensions.PLAUSIBLE), 0),
            "typical_percentile": assignment.confidence.get(Variable(fact.index, Dimensions.TYPICAL), 0),
            "remarkable_percentile": assignment.confidence.get(Variable(fact.index, Dimensions.REMARKABLE), 0),
            "salient_percentile": assignment.confidence.get(Variable(fact.index, Dimensions.SALIENT), 0),
        })
    df_facts = pd.DataFrame(data)
    del data
    n = df_facts.shape[0]
    print("Normalizing columns...")
    pbar = tqdm(total=20)
    for column in [
            "plausible_percentile",
            "typical_percentile",
            "remarkable_percentile",
            "salient_percentile",
            "evidence_plausible",
            "evidence_typical",
            "evidence_remarkable",
            "evidence_salient",
            "cue_joint",
            "cue_necessity",
            "cue_sufficiency",
            "cue_implication",
            "cue_implication",
            "cue_entailment",
            "cue_contradiction",
            "cue_entropy"
        ]:
        df_facts = df_facts.sort_values(by=column)
        df_facts[column] = [i / (n-1) for i in range(n)]
        pbar.update(1)
    for column in ["plausible", "typical", "remarkable", "salient"]:
        values = list()
        a, b = df_facts[column].min(), df_facts[column].max()
        for index, row in df_facts.iterrows():
            values.append((row[column] - a) / (b - a))
        df_facts[column] = values
        pbar.update(1)
    pbar.close()
    print("Gathering partition...")
    data = list()
    with open(partition_file) as file:
        for line in tqdm(file.readlines()):
            count, *indices = list(map(int, line.strip().split("\t")))
            subjects = set([kb[j].subject for j in indices])
            properties_all = list(set([kb[j].property for j in indices]))
            local_indices = [similarity.index[p] for p in properties_all]
            local_matrix = similarity.matrix[local_indices][:, local_indices]
            for i in range(count):
                fact = kb[indices[i]]
                if indices[i] not in selected_indices:
                    continue
                property_index_self = similarity.index[fact.property]
                parents = list()
                children = list()
                siblings = list()
                if fact.subject in taxonomy.nodes:
                    parents = [
                        "{neighbor}:{weight}".format(
                            neighbor=neighbor,
                            weight=taxonomy.weight(fact.subject, neighbor),
                        )
                        for neighbor in subjects.intersection(taxonomy.predecessors(fact.subject))
                    ]
                    children = [
                        "{neighbor}:{weight}".format(
                            neighbor=neighbor,
                            weight=taxonomy.weight(fact.subject, neighbor),
                        )
                        for neighbor in subjects.intersection(taxonomy.successors(fact.subject))
                    ]
                    siblings = [
                        "{neighbor}:{weight}".format(
                            neighbor=neighbor,
                            weight=taxonomy.weight(fact.subject, neighbor),
                        )
                        for neighbor in subjects.intersection(taxonomy.siblings(fact.subject))
                    ]
                properties = list()
                for j, k in zip(*local_matrix.nonzero()):
                    if local_indices[j] != property_index_self:
                        continue
                    properties.append(properties_all[k] + ":" + str(local_matrix[j, k]))
                data.append({
                    "index": indices[i],
                    "parents": ";".join(parents),
                    "children": ";".join(children),
                    "siblings": ";".join(siblings),
                    "properties": ";".join(properties),
                })
    df_partition = pd.DataFrame(data)
    df = df_facts.set_index("index").join(df_partition.set_index("index"), on="index", how="outer")
    df.to_csv(output.path("demo.csv"), index=False)

modules = {
    "pipeline": ModuleWrapper(pipeline, 1),
    "clone_inputs": ModuleWrapper(clone_inputs, 2, 2),
    "kb_extender": ModuleWrapper(kb_extender, 2),
    "bulk_kb_extender": ModuleWrapper(bulk_kb_extender, 4, 4),
    "bulk_pipeline": ModuleWrapper(bulk_pipeline, 6),
    "bulk_gatherer": ModuleWrapper(bulk_gatherer, 2, 2),
    "bulk_tuner": ModuleWrapper(bulk_tuner, 8, 8),
    "partitioner": ModuleWrapper(partitioner, 6, 6),
    "bulk_process": ModuleWrapper(bulk_process, 7, 7),
    "prettify_tracker": ModuleWrapper(prettify_tracker, 2, 2),
    "kb_builder": ModuleWrapper(kb_builder, 3),
    "disambiguator": ModuleWrapper(disambiguator, 1, 1),
    "kb_merge": ModuleWrapper(kb_merge, 3, 3),
    "tracker": ModuleWrapper(tracker, 2, 2),
    "mturk_annotation": ModuleWrapper(mturk_annotation, 3),
    "pair_sampler": ModuleWrapper(pair_sampler, 3, 3),
    "pair_evaluator": ModuleWrapper(pair_evaluator, 4),
    "bayesian_tuner": ModuleWrapper(bayesian_tuner, 5),
    "dialogue_generator": ModuleWrapper(dialogue_generator, 2, 2),
    "dialogue_generator_batch": ModuleWrapper(dialogue_generator_batch, 3, 3),
    "demo": ModuleWrapper(demo, 5, 5),
}
