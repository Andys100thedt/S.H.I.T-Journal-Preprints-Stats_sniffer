import requests,time,json,pickle

from enumerate_configuration import _DEFAULT_CONFIGURATION
from post_processing.stat_accumu import StatFlowDataset, StatFrame

def update():
    params = {
        "select": "*",
        "order": "created_at.desc",
        "offset": 0,
        "limit": _DEFAULT_CONFIGURATION.limitN,
        "apikey": _DEFAULT_CONFIGURATION.api_key,
    }

    payload = requests.get("https://bcgdqepzakcufaadgnda.supabase.co/rest/v1/preprints_with_ratings?",params=params,headers=_DEFAULT_CONFIGURATION.headers)
    content = payload.json()

    with open("stats/meta-id-refmap", 'r') as f:
        refmap: dict[str, dict] = json.loads(f.read())
    with open("stats/dataset.bin", 'rb') as f:
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

        if preprint_id not in refmap: refmap.update({preprint_id: preprint_meta})  # once-initiated-meta-map
        if preprint_id not in dataset.dataset.keys():
            dataset.dataset.update({preprint_id: [preprint_stat_frame]})
        else:
            dataset.dataset[preprint_id].append(preprint_stat_frame)

    with open("stats/meta-id-refmap", 'w') as f:
        json.dump(refmap, f)
    with open("stats/dataset.bin", 'wb') as f:
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
