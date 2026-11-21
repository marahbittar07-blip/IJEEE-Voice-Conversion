# Release status — 20 November 2026

This is a concrete author-review package, not a published/fully GPU-validated release.

## Completed locally

- Organized four revision execution notebooks and archived exact executed predecessors with outputs. Archived older experiments separately; MLPG excluded from evaluated code.
- Added configurable DATA_ROOT/RUN_DIR, with new reproduction output folder by default. Original result CSVs remain unchanged.
- Fixed E9 schema and strict atomic writer in main; separated recovery cells. Organized timing-only notebook with session resumption; fixed extra-run export filename.
- Checked Python syntax for all execution code cells and scripts. Compared core inference/scoring function ASTs with archived originals: unchanged.
- Tested main writer with 280 synthetic rows, NaN/non-cascade timings, column reordering, quoted multiline transcripts, and rejection of corrupt/mismatched input without modifying its bytes.
- Ran CPU repository validation and deterministic saved-result analysis. Recovered selection tau=0.1/10 steps and 28.66% latency saving. Saved Tables I–VI, new plots and settings/input hashes in analysis_outputs.
- Identified Table V as independent reconstruction: original bootstrap script/seed/options unavailable; author reconciliation required.
- Added local-export data staging script, input-layout preflight, data/run instructions, provenance and change notes. No audio/checkpoints redistributed.

## Still required before claiming full public reproducibility

1. Test the original dependency pins, staged input paths, model execution and scoring in clean Colab sessions; no GPU run was performed here.
2. A reader starting from original public corpora still needs a tested preparation pipeline for prepared inputs and legacy outputs. Current staging supports authors' private ZIP exports only.
3. Resolved: `scripts/paired_stats_r10.py` is the exact script behind the R10 statistics and reproduces all 18 rows of Table V; `analyze_results.py` remains as an independent check. New plots are not exact manuscript replicas.
4. Licence set: MIT for code, CC BY 4.0 for results and documentation (`LICENSE`, `LICENSE-results.md`). Authors confirm citation/release metadata; no DOI or repository URL is invented by this package.
5. After author review, publish the reviewed GitHub repository and archive a release on Zenodo; add its DOI to the paper.

The archive may be sent to the supervisor now for review with these limitations stated. It should not be presented as an already-tested one-click reproduction.
