import math
import pickle

from post_processing.stat_accumu import IntegratedDataset, IntegratedStatClue, StatResultDatabase, IntegratedStatResult

if __name__ == "__main__":
    path = "stats/integrated_dataset_o_-1_cp_1772516670.470826.bin"
    with open(path,'rb') as dataset:
        integration_set: IntegratedDataset = pickle.load(dataset)
    result_database: StatResultDatabase = StatResultDatabase({})

    for idx,key in enumerate(integration_set.dataset.keys()):
        preprint: IntegratedStatClue = integration_set.dataset[key]

        result: IntegratedStatResult = IntegratedStatResult(
            preprint.linear_offset,
            math.log10(preprint.variation_weighted+2)*math.log10(preprint.latest_rated_count-4.3) if preprint.variation_weighted >= 1e-07 else 0.0,
            preprint.latest_score_weighted*math.log(preprint.latest_rated_count-3.8),
        )
        (result_database.database.update({key: result}))

    max_hotness = max([stat.hotness for stat in result_database.database.values()])
    max_controversy = max([stat.controversy for stat in result_database.database.values()])
    controversy_scale_ratio = max_hotness / max_controversy

    for idx,key in enumerate(result_database.database.keys()):
        preprint: IntegratedStatResult = result_database.database[key]

        result: IntegratedStatResult = IntegratedStatResult(
            preprint.rising*100,
            preprint.controversy*controversy_scale_ratio - preprint.hotness, # Differentially tuned controversy
            preprint.hotness,
        )
        (result_database.database.update({key: result}))
        print(preprint)
        print({key: result})
        print()

    with open(path.replace("integrated_dataset_","result_database_"), 'wb') as f:
        pickle.dump(result_database, f)