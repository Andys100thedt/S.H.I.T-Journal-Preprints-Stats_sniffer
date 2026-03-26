import requests,time,json,pickle

from enumerate_configuration import _DEFAULT_CONFIGURATION
from post_processing.stat_accumu import StatFlowDataset, StatFrame

def recursive_fetching(offset: int = 0, fetch_result=None, _recursive_depth: int = 0):
    if fetch_result is None:
        fetch_result = []
    params = {
        "select": "*",
        "order": "created_at.desc",
        "offset": offset,
        "limit": _DEFAULT_CONFIGURATION.limitN,
        "apikey": _DEFAULT_CONFIGURATION.api_key,
    }

    payload = requests.get("https://bcgdqepzakcufaadgnda.supabase.co/rest/v1/preprints_with_ratings?", params=params, headers=_DEFAULT_CONFIGURATION.headers)
    fetch_result += payload.json()
    offset += 1000
    if len(fetch_result) == 1000:
        return recursive_fetching(offset, fetch_result, _recursive_depth+1)
    else:
        return fetch_result, _recursive_depth

def update():
    content,depth = recursive_fetching()
    print("Fetch complete with depth", depth,",length", len(content))
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
        preprint_score_weighted = preprint_meta["weighted_score"]
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
