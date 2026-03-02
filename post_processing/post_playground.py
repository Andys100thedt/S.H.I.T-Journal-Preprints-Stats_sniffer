import pickle,time,matplotlib.pyplot as plt

import numpy

from post_processing.post_processing_utils import clamp_and_sort, time_weighted_mse, jump_rate
from post_processing.stat_accumu import StatFlowDataset, IntegratedDataset, IntegratedStatClue, _STATIC_FRAME, \
    IntegratedStatResult, StatResultDatabase
from enumerate_configuration import _DEFAULT_CONFIGURATION

def plot_results_snapshot(path: str):
    with open(path, 'rb') as database:
        result_db: StatResultDatabase = pickle.load(database)

    id_idx = range(len(result_db.database.values()))
    rising = [data.rising for data in result_db.database.values()]
    controversy = [data.controversy for data in result_db.database.values()]
    hotness = [data.hotness for data in result_db.database.values()]

    plt.figure(figsize=(8, 6))
    plt.plot(id_idx, rising, label='Rising factor', marker='o', linestyle='-')
    plt.plot(id_idx, controversy, label='Controversy factor', marker='s', linestyle='--')
    plt.plot(id_idx, hotness, label='Hotness score', marker='^', linestyle=':')

    plt.xlabel('id_idx')
    plt.ylabel('Values')
    plt.title('Plot of result')
    plt.legend()
    plt.grid(True)

    plt.show()

def flow_examination(preprint_id: str):
    with open("../stats/dataset.bin", 'rb') as f:
        dataset: StatFlowDataset = pickle.load(f)

    for idx, stat in enumerate(dataset.dataset[preprint_id]):
        print(stat)

def id_str4id_idx(path: str,id_idx: int) -> str:
    with open(path, 'rb') as database:
        result_db: StatResultDatabase = pickle.load(database)
    return list(result_db.database.keys())[id_idx]

def result_outlier_culling_by_rising(path: str):
    # Not useful for now
    with open(path, 'rb') as database:
        result_db: StatResultDatabase = pickle.load(database)

    vl_stats_map = result_db.database
    vl_stat_ks = list(result_db.database.keys())
    rising = numpy.array([vl_stats_map[stat_k].rising for stat_k in vl_stat_ks])
    result = float(numpy.percentile(rising, 85))
    print(pow(result,2))

    outliers = [stat_k if vl_stats_map[stat_k].rising > result*2 else -114514 for stat_k in vl_stat_ks]
    ignored_popped_value = [result_db.database.pop(vl_stat_ks[outliers_idx]) if outliers[outliers_idx] != -114514 else None for outliers_idx in range(len(outliers))]
    with open(path, 'wb') as database:
        pickle.dump(result_db,database)

if __name__ == "__main__":
    db_path = "../stats/result_database_o_-1_cp_1772454892.948831.bin"
    #flow_examination("0928f19e-927f-4bd5-ad22-1bc4a9f3e37f")
    plot_results_snapshot(db_path)
    #print(id_str4id_idx(db_path, 107))
