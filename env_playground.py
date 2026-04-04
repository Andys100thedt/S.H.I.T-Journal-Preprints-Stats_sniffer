import requests

import lifecycle,os,json,pickle

from post_processing.stat_accumu import StatFlowDataset
from enumerate_configuration import _DEFAULT_CONFIGURATION

def print_url():
    params = {
        "limit": _DEFAULT_CONFIGURATION.limitN,
    }
    payload = requests.get(_DEFAULT_CONFIGURATION.shit_articles_api_endpoint, params=params,headers=_DEFAULT_CONFIGURATION.headers)
    print(payload.url)

def initialize_refmap():
    with (open("stats/meta-id-refmap", 'w')) as f:
        json.dump({}, f)
def initialize_flow_dataset():
    with open("stats/dataset.bin", 'wb') as f:
        pickle.dump(StatFlowDataset({}), f)

if __name__ == "__main__":
    print("deprecated supabase publishable key:", os.getenv("SHIT_API_KEY")) #deprecated
    print_url()
    lifecycle.update()