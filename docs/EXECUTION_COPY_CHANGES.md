# Execution-copy changes

Original model calls/seeds/scoring were retained. Exact predecessors are archived; no archived results were changed.

02: removed recovery/probes and post-timing scoring; retained setup, holdout preparation, model warmup and timing. Added runtime session ID and per-session resume keys, without changing measured model calls.

03: cleared outputs and export follows RESULTS_PATH from the current E14 run, replacing the stale hardcoded filename. Inference remains unchanged.

YourTTS: filename retained; exact executed original archived; output clearing and runtime path overrides only; both original sessions and CUDA speaker-encoder fix preserved.

All four execution copies now use a distinct reproduction output directory and configurable input root. Ten independent Kathleen clips are required where a count check existed. Historical output files remain prerequisites for E7/reproduction check. Runtime installation/GPU behavior has not been tested here.


Current status supersedes earlier next-work notes: see RELEASE_STATUS.md. All four organized copies are now supplied; independent CPU analysis is included. Full GPU/public-data reproduction is still unverified.
