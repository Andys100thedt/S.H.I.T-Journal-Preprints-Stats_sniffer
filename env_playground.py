import lifecycle,os,json,pickle

from post_processing.stat_accumu import StatFlowDataset

if __name__ == "__main__":
    print(os.getenv("SHIT_API_KEY"))
    """
    with (open("stats/meta-id-refmap",'w')) as f:
        json.dump({},f)
    """
    with open("stats/dataset.bin", 'wb') as f:
        pickle.dump(StatFlowDataset({}),f)
    #lifecycle.update()