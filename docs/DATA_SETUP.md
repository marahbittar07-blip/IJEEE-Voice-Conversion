# Runtime data setup

The public package contains metadata, not audio or checkpoints. Do not upload the private runtime-data folder with the repository. This guide supports staging the authors' original local ZIP exports; it is not an automatic public-corpus download/reconstruction implementation.

## Public input identities

Use Joe 1.0 and Kathleen 1.0 as cited by manuscript R10, with IDs in `data/file_ids.csv` and the full provenance in the manifests. VCTK 0.92 is prepared by main code Cell 12. OpenVoice and Seed-VC upstream repository/commit URLs are embedded in installation cells; Seed-VC model assets are loaded by its pinned inference implementation. The OpenVoice converter config is archived in this repo, while its checkpoint must be supplied separately. The authors' supplied `models.zip` can stage the exact recorded copy.

## Authors' existing exports

Keep the following files privately outside the repository:

- selected_hybrid_data(1).zip (six prepared tuning/reference WAVs plus manifest)
- kathleen_independent_refs.zip (ten prepared independent target WAVs plus manifest)
- final_holdout_data.zip (ten original source WAVs plus metadata)
- final_holdout_data_40.zip (forty source WAVs plus metadata)
- final_hybrid_comparison.zip (historical converted WAVs, metrics and embeddings)
- models.zip (OpenVoice converter config/checkpoint)
- joe.tar.gz (original source archive)

For a fresh private staging folder, run from the repository root, substituting your local paths:

```bash
python scripts/prepare_local_inputs.py \
  --data-root /path/outside/repo/IJEEE_VC_data \
  --selected '/path/to/selected_hybrid_data(1).zip' \
  --eval /path/to/kathleen_independent_refs.zip \
  --holdout10 /path/to/final_holdout_data.zip \
  --holdout40 /path/to/final_holdout_data_40.zip \
  --legacy /path/to/final_hybrid_comparison.zip \
  --models /path/to/models.zip \
  --joe /path/to/joe.tar.gz
python scripts/preflight_inputs.py --data-root /path/outside/repo/IJEEE_VC_data
```

The staging script copies WAV/CSV/JSON files from the named archive subfolders, skips embeddings/caches, copies only the converter config/checkpoint from models.zip, and rebases `prepared_wav` paths in private runtime metadata. It rejects replacement of different existing files. It does not decode/unpickle model weights, download anything, generate audio or alter archived repository metadata. Prefer a fresh staging folder. File-layout preflight does not establish waveform identity or successful GPU execution.

For Colab, DATA_ROOT normally refers to `/content/drive/MyDrive/IJEEE_VC_data`; this path is not a Windows path. Stage into the corresponding Drive folder or adapt the runtime configuration. Do not mix prepared WAVs from the ten-sentence export with those in the forty-sentence export: IDs/transcripts match for the first ten, but exported audio bytes were found to differ.

## Required input layout

| Under DATA_ROOT | Content |
|---|---|
| `selected_hybrid_data/` | joe_source_01–03, kathleen_reference, kathleen_conditioning_ref_02/03 WAVs |
| `kathleen_independent_refs/` | kathleen_eval_01–10 WAVs |
| `final_holdout_data/` | holdout_metadata.csv and ten source WAVs |
| `final_holdout_data_40/` | holdout40_metadata.csv and forty source WAVs |
| `final_hybrid_comparison/` | historical OpenVoice, Seed-only, reference and optimized output WAV folders |
| `models/OpenVoiceV2/converter/` | config.json and checkpoint.pth |
| `joe.tar.gz` | original source corpus archive |

## Remaining public-reproduction dependency

A third-party reader who has only the original public corpora still needs an independently tested preparation script to recover all prepared inputs and historical output WAVs. This package documents the authors' local-export route and identifies this gap rather than bypassing reproduction checks. The original generation notebooks may help reconstruct historical outputs, but are not yet a tested automated preparation pipeline. Report this limitation to the authors before claiming complete fresh-public-data reproducibility.
