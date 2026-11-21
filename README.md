# Stage-Wise Parameter Selection for Cascaded Zero-Shot Voice Conversion

Allam Mousa, Sara Antari, Marah Bittar.

**Author-review package — prepared 20 November 2026.** This repository organizes executed research records supporting manuscript R10 and provides cleaned execution copies plus a CPU analysis of saved results. It has not undergone an end-to-end fresh Colab/GPU rerun during packaging. Review [docs/RELEASE_STATUS.md](docs/RELEASE_STATUS.md) before publication.

## Fast start: analyze the existing results (no GPU or audio required)

From the repository root:

```bash
python -m pip install -r requirements-analysis.txt
python scripts/validate_repository.py
python scripts/analyze_results.py
python scripts/paired_stats_r10.py
```

CPU validation and analysis were run during packaging using the versions pinned in `requirements-analysis.txt`. The analysis exports Tables I–VI as CSV, an explicit selection audit, paired confidence intervals, new plots, and a manifest of inputs/settings into `analysis_outputs/`. Example outputs from this run are included there. Original result CSVs are never overwritten.

**Exact R10 statistics.** `python scripts/paired_stats_r10.py` runs the script that produced the statistics in manuscript R10 (bootstrap seed 2026, 20,000 resamples) and writes them to `analysis_outputs/r10_exact/`; it reproduces all 18 rows of Table V. `scripts/analyze_results.py` is an independent check with a different seed: means, SDs and p-values agree, and confidence-interval limits differ only in the third decimal. The plots in `analysis_outputs/` are new renderings of the archived data, not copies of the manuscript graphics.

## Systems and execution notebooks

| Notebook | Systems/experiments |
|---|---|
| `notebooks/01_Revision_Main_Experiments.ipynb` | OpenVoice alone; Seed-VC at 10 and 25 steps; OpenVoice→Seed-VC cascades; 5×5 grid, 40 holdout, extra references, VCTK |
| `notebooks/02_Revision_Second_Session_Timing.ipynb` | Independent-session timing on ten holdout sentences for four systems |
| `notebooks/03_Revision_Tau01_and_Reverse_Order.ipynb` | Final tau=0.1/10-step cascade and reverse Seed-VC→OpenVoice at two settings |
| `notebooks/IJEEE_yourtts_holdout.ipynb` | Session A: Whisper-large-v3→YourTTS generation/timing; fresh Session B: common scoring |

YourTTS here is ASR-mediated resynthesis, not direct waveform conversion. Both stages of each cascade use the same target conditioning reference. MLPG is excluded from evaluated repository systems.

Execution copies have cleared outputs so historical evidence is not mistaken for new execution. Exact executed notebooks and their saved outputs are preserved under `archive/revision_executed/`. The original YourTTS filename is retained. Prior ten-sentence/sweep experiments are under `archive/original_experiments/`; they are supporting history, not additional required revision steps. The unmodified original template is under `archive/reference_templates/`.

## Layout

| Path | Contents |
|---|---|
| `data/` | File IDs, source transcripts, holdout metadata, reference/evaluation manifests |
| `results/revision/` | Immutable grid, holdout, reference, timing, VCTK and E14 results |
| `results/yourtts/` | Immutable YourTTS generation/scoring, formats and environment |
| `results/original/` | Historical ten-sentence and sweep results |
| `configs/openvoice_v2/` | Recorded converter config, without weights |
| `scripts/` | CPU analysis, repository checks, runtime data staging and input preflight |
| `analysis_outputs/` | Generated example analysis, separate from original results |
| `docs/` | Input setup, run order, changes, provenance, limitations and reviewer notes |

## Before running models

Follow [docs/DATA_SETUP.md](docs/DATA_SETUP.md), then [docs/RUN_ORDER.md](docs/RUN_ORDER.md). Audio and weights are not distributed here. The notebooks have historical package pins that still need clean-session installation testing. They require the recorded Joe/Kathleen inputs, checkpoint files, and legacy output WAVs for the historical reproduction check. VCTK is handled by the notebook's original corpus download/preparation cell.

Each notebook has a configuration cell with DATA_ROOT and RUN_DIR. Edit both consistently after restarting the runtime. DATA_ROOT is private runtime audio/model storage. RUN_DIR defaults to a separate reproduction folder, not the immutable `results/` archive. Use the same RUN_DIR when resuming or linking YourTTS A/B; choose a different folder for a separate reproduction.

## Result interpretation

Grid: 375 observations (25 configurations × 3 sentences × 5 seed sets). Main holdout E9: 280 (7×40). E14 extra run: 120 (3×40). Alternate references: 240. VCTK: 150. Timing: 80 across two sessions. YourTTS scoring: 40. E7 has 40 historical outputs, meaning ten sentences × four systems, not forty sentences per system.

`Selected cascade (tau 0.5, 10)` is the earlier selection. R10's final selected cascade is tau=0.1/10 from E14. These results must not be silently relabeled. GPU timing may differ by session; seed-controlled audio/metrics may still vary by platform. [docs/TABLE_PROVENANCE.md](docs/TABLE_PROVENANCE.md) maps table inputs.

## Upstream versions and authorship

OpenVoice commit: `74a1d147b17a8c3092dd5430504bd83ef6c7eb23` (V2 converter).
Seed-VC commit: `51383efd921027683c89e5348211d93ff12ac2a8`.
Generation/scoring environment details are preserved in result JSONs; YourTTS generation used a separate environment. `requirements-analysis.txt` is for CPU analysis only, not GPU inference.

Raw/converted audio, embeddings and model weights are excluded. Dataset/model terms remain those of their owners. The authors' code is released under the MIT License (`LICENSE`), and their results and documentation under CC BY 4.0 (`LICENSE-results.md`). In the archived records, the private Google Drive folder name was replaced by `IJEEE_VC_data`; only that folder name changed. No DOI or public repository address is asserted by this review package. Authors should review and reconcile outstanding items, then publish a reviewed release and archive it on Zenodo.
