# SHIT-Journal-Preprints-Stats_sniffer

A project to consistently update statistics and discover the most interesting preprints published on the journal 《SHIT》.

## Features

- **Automated Statistics Update:** Regularly scans the journal for new preprints, updating key stats automatically.
- **Highlighting Preprints:** Helps surface and highlight the most interesting or noteworthy work, based on automated analysis.
- **Modular Processing:** Flexible post-processing, ranking, and result formatting.

## Structure

```
.
├── .idea/                   # IDE settings (safe to ignore)
├── _daemon.py               # Main daemon or entry point for background/stat update processes
├── enumerate_configuration.py # Loads and manages configuration for the stats sniffer
├── env_playground.py        # Environment handling and experimentation
├── lifecycle.py             # Controls job/task lifecycle, init, teardown, etc.
├── post_processing.py       # Handles processing of scraped data after main tasks are done
├── post_processing/         # Additional scripts/assets for post-processing
├── result_algorithm.py      # Core logic for generating, ranking, or summarizing preprint statistics
```

## Usage

1. **Setup your environment**
   - Make sure you have Python installed (also make sure you meet all dependency requirements as there are no requirements.txt).
   - Configure `enumerate_configuration.py` if you will.
   - Add an environment variable "SHIT_API_KEY" in your system's environment, apikey could be found using your own 《SHIT》 account and by packet analysis.
   - *or you can however just directly code your key string into the configuration, who cares except yourself*

2. **Run the Stats Sniffer**
   - Before starting: run `env_playground.py` to generate initialized dataset files required for the rest parts of the project
   - Typical entry point: `_daemon.py`  
     ```
     python _daemon.py
     ```

4. **Extend or Customize**
   - Tweak `result_algorithm.py` to change how preprints are selected/ranked.
   - Add custom post-processing steps in `post_processing.py` or the `post_processing/` folder.
   - For testing or experiments, use `env_playground.py` and `post_processing/post_playground.py`.

5. **Output Structure**
   - `lifecycle.py`: attach the newest data captured when running and attach them to `/stats/dataset.bin`(binary raw dataset) and `/stats/meta-id-refmap`(.json map |id_str|->|metadata dict|)
   - `post_processing.py`: reads all data in dataset.bin and calculating statistical metrics for each preprint subject. Result stored in `/stats/integrated_dataset_0_-1_cp_${time.time()}.bin`
   - `result_algorithm.py`: reads the output file of `post_processing.py` specified by file-scoped variable `path` declared **MANUALLY**(which means to you have to change it overtime), saves a similar file with `post_processing.py`
   - Results would be able to visualize when the output of `result_algorithm.py` was specified in `post_processing/post_playround.py`.
   - Explore the project to figure out more.

6. **Configuration**
   - `interval: float`: interval between each `lifecycle.py` logs and write records of data into the file; default: 60*5 sec
   - `lifecycle: float`: length of period for `_daemon.py` to restart `lifecycle.py` in order to avoid increasingly high memory usage; default: 1200 sec
   - `datetime_critical: float`: threshold for `post_processing.py` but not `lifecycle.py` to reject preprints which are published too early; default: before 00.00 UTC+8 Saturday of the last week(this week if you're on Saturday or Sunday themselves) when the configuration is loaded
   - `limitN: int`: a parameter passed onto api call about how much pieces of preprints' data you are going to fetch in a single call; default: 50 (maximum possible for latest shit api impl, Apr 3 2026)
   - `count_threshold: int`: threshold of `latest_rated_count` for `post_processing.py` but not `lifecycle.py` to reject preprints with few people rated, less than but not included; default: 6
   - `apikey: str, headers: dict`: parameters passed onto api call;

## Contributing

Contributions (code, new features, bug reports) are warmly welcomed! Feel free to fork, file issues, or submit PRs. Though my time is always pretty limited.

## About 《SHIT》

《SHIT》 stands for Science. Humanities. Information. Technology.  
Or originally: Study of Higher and Inner Trash.  
A tongue-in-cheek community for all creative works.
Website: [SHIT JOURNAL](https://shitjournal.org/)

## See also

Downstream project: [SSMH](https://github.com/SHIT-Journal-stats/SHIT-Journal-stats.github.io/)

---

*This project is still under construction and open to *all* ideas, no matter how ridiculous!*
