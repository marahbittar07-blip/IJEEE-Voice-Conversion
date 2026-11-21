# R10 table provenance

| Paper table | Input result files | Producing notebook |
|---|---|---|
| I | `results/revision/E9_holdout40.csv`, `E14_extra_20261116_202913_17be5126.csv`; `results/yourtts/E15_yourtts_holdout40.csv` | Main, extra-run, YourTTS |
| II | `results/revision/E8_grid_5x5_seeds.csv` | Main, code Cell 8 |
| III | Same E8 file, grouped by steps or tau; RTF = latency/src_duration | Main, aggregation provided by scripts/analyze_results.py |
| IV | E9 plus E14 final tau=0.1 configuration | Main and extra-run |
| V | Paired by sample: E14 tau=0.1 minus E9 comparison systems | scripts/paired_stats_r10.py (exact R10 script, seed 2026); scripts/analyze_results.py gives an independent check |
| VI | E11 session timing, E10 alternate references, E14 reverse order, E12 VCTK pairs | Timing, main, extra-run |

Historical results in `results/original` are for earlier experiments and should not replace these current tables. `results/revision/holdout40_metadata.csv` is retained as part of the saved run; the copy under `data/` is the input metadata record.

The earlier numerical audit found 339 rounded means/SDs/grid values/differences consistent with the result CSVs. It did not certify exact bootstrap random seeds, every p-value, figure production, or all narrative claims. The original table-V/figure script has not been supplied. A regenerated analysis must explicitly state random seeds, software versions, test options and rounding rather than claim to recover an unavailable script.


The current package includes scripts/analyze_results.py and its example analysis_outputs. The prior statement about the unavailable original script remains true; the newly provided script is explicitly an independent reconstruction, not a recovered historical script.


Update: the original Table V script is now included as `scripts/paired_stats_r10.py`. It reproduces every row of R10 Table V exactly (`analysis_outputs/r10_exact/holdout40_paired_tests.csv`).
