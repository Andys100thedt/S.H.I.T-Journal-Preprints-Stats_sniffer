import requests

import lifecycle,os,json,pickle

from post_processing.stat_accumu import StatFlowDataset
from enumerate_configuration import _DEFAULT_CONFIGURATION

def print_url():
    params = {
        "select": "*",
        "order": "created_at.desc",
        "offset": 0,
        "limit": _DEFAULT_CONFIGURATION.limitN,
        "apikey": _DEFAULT_CONFIGURATION.api_key,
    }
    payload = requests.get("https://bcgdqepzakcufaadgnda.supabase.co/rest/v1/preprints_with_ratings?", params=params,headers=_DEFAULT_CONFIGURATION.headers)
    print(payload.url)

def initialize_refmap():
    with (open("stats/meta-id-refmap", 'w')) as f:
        json.dump({}, f)
def initialize_flow_dataset():
    with open("stats/dataset.bin", 'wb') as f:
        pickle.dump(StatFlowDataset({}), f)

def force_update_metadata():
    refmap = {}
    params = {
        "select": "*",
        "order": "created_at.desc",
        "offset": 0,
        "limit": _DEFAULT_CONFIGURATION.limitN,
        "apikey": _DEFAULT_CONFIGURATION.api_key,
    }

    payload = requests.get("https://bcgdqepzakcufaadgnda.supabase.co/rest/v1/preprints_with_ratings?", params=params,
                           headers=_DEFAULT_CONFIGURATION.headers)
    content = payload.json()
    for preprint in content:
        refmap.update({preprint["id"]: preprint})

    with open("stats/meta-id-refmap", 'w') as f:
        json.dump(refmap, f)

if __name__ == "__main__":
    print(os.getenv("SHIT_API_KEY"))
    print_url()
    #force_update_metadata()
    lifecycle.update()
    #lifecycle.update()