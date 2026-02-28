import pickle,time,json

from post_processing.post_processing_utils import clamp_and_sort, time_weighted_mse, jump_rate
from post_processing.stat_accumu import StatFlowDataset, IntegratedDataset, IntegratedStatClue, _STATIC_FRAME
from enumerate_configuration import _DEFAULT_CONFIGURATION
from datetime import datetime, timezone

def iso8601_to_ts(iso8601_str: str) -> int:
    dt = datetime.fromisoformat(iso8601_str)
    timestamp = dt.timestamp()
    return int(timestamp)

if __name__ == "__main__":
    with open("stats/dataset.bin", 'rb') as f:
        dataset: StatFlowDataset = pickle.load(f)
    with open("stats/meta-id-refmap", 'r') as f:
        refmap: dict[str, dict] = json.loads(f.read())
    integrated_dataset = IntegratedDataset({})
    offset = -1

    ids: list = list(dataset.dataset.keys())
    for idx,preprint in enumerate(dataset.dataset.values()):
        sorted_clamped_raw = clamp_and_sort(offset, preprint)
        mse_weighted,mse_plain = time_weighted_mse(sorted_clamped_raw)
        jump_rate_plain = jump_rate(sorted_clamped_raw)

        if sorted_clamped_raw[-1].score_weighted == _STATIC_FRAME.score_weighted or sorted_clamped_raw[-1].rated_count < _DEFAULT_CONFIGURATION.count_threshold:
            continue
        if iso8601_to_ts(refmap[ids[idx]]["created_at"]) <= _DEFAULT_CONFIGURATION.datetime_critical:
            continue

        clue_frame: IntegratedStatClue = IntegratedStatClue(
            sorted_clamped_raw[-1].score_plain,
            sorted_clamped_raw[-1].score_weighted,
            sorted_clamped_raw[-1].rated_count,
            mse_plain,
            mse_weighted,
            jump_rate_plain
        )
        integrated_dataset.dataset.update({ids[idx]: clue_frame})
        print({ids[idx]: clue_frame})

    with open("stats/integrated_dataset_o_"+str(offset)+"_cp_"+str(time.time())+".bin", 'wb') as f:
        pickle.dump(integrated_dataset, f)
    input("Press to terminate...")