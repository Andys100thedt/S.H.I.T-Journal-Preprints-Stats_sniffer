from typing import Tuple

import requests,time,json,pickle

from enumerate_configuration import _DEFAULT_CONFIGURATION
from post_processing.stat_accumu import StatFlowDataset, StatFrame

def recursive_fetching():
    result,count = [],0
    latrine = recursive_fetching_each_zone("latrine")
    result += latrine[0]; count += latrine[1]
    septic = recursive_fetching_each_zone("septic")
    result += septic[0]; count += septic[1]
    stone = recursive_fetching_each_zone("stone")
    result += stone[0]; count += stone[1]
    sediment = recursive_fetching_each_zone("sediment")
    result += sediment[0]; count += sediment[1]

    return result,count

def recursive_fetching_each_zone(zone: str) -> Tuple[list, int]:

    fetch_result = []

    params = {
        "zone": zone,
        "sort": "newest",
        "page": "1",
        "limit": _DEFAULT_CONFIGURATION.limitN,
    }

    payload = requests.get(_DEFAULT_CONFIGURATION.shit_articles_api_endpoint, params=params, headers=_DEFAULT_CONFIGURATION.headers)
    fetch_respond = payload.json()

    if fetch_respond["status"] == "success":
        fetch_result += fetch_respond["data"]
        for page_idx in range(int(fetch_respond["total_pages"])-1):
            fetch_result += fetch_respond["data"]
    return fetch_result, int(fetch_respond["total_pages"])

def update():
    content,page_count = recursive_fetching()
    print(f"Fetch complete with {page_count} pages and {len(content)} articles(preprints)")
    """
    with open("stats/meta-id-refmap", 'r') as f:
        refmap: dict[str, dict] = json.loads(f.read())
    """
    refmap = {}
    try:
        with open("stats/dataset.bin", 'rb') as f:
            dataset: StatFlowDataset = pickle.load(f)
    except EOFError as ignored:
        print("error-Dataset file corrupted, switching to the back-up file")
        with open("stats/dataset_backup.bin", 'rb') as f:
            dataset: StatFlowDataset = pickle.load(f)

    for preprints in content:
        preprint_meta: dict = preprints
        preprint_id = preprint_meta["id"]
        preprint_score_plain = preprint_meta["avg_score"]
        #preprint_score_weighted = preprint_meta["weighted_score"]
        preprint_score_weighted = -1
        preprint_rated_count = preprint_meta["rating_count"]
        preprint_stat_frame = StatFrame(
            time.time(),
            preprint_score_plain,
            preprint_score_weighted,
            preprint_rated_count,
        )

        refmap.update({preprint_id: preprint_meta})  # updating-meta-map which captures preprints deleted or missingno
        if preprint_id not in dataset.dataset.keys():
            dataset.dataset.update({preprint_id: [preprint_stat_frame]})
        else:
            dataset.dataset[preprint_id].append(preprint_stat_frame)

    with open("stats/meta-id-refmap", 'w') as f:
        json.dump(refmap, f)
    with open("stats/dataset.bin", 'wb') as f:
        pickle.dump(dataset, f)
    with open("stats/dataset_backup.bin", 'wb') as f:
        pickle.dump(dataset, f)

if __name__ == '__main__':

    last_delta_t = None
    print("Lifecycle started")
    while True:
        delta_t = time.time() % _DEFAULT_CONFIGURATION.interval
        if last_delta_t is not None:
            if delta_t < last_delta_t and last_delta_t > _DEFAULT_CONFIGURATION.interval*0.9:
                print("Updating...")
                update()
                print("Updated at delta_t="+str(round(delta_t,5)))
        last_delta_t = delta_t
        time.sleep(.01)
