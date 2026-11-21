# Run order

## A. CPU verification and analysis (tested during packaging)

Use the commands in README. No T4 or recordings are needed. Analysis reads only archived CSVs and writes to analysis_outputs. Table V reconstruction and plots are explicitly identified as new analysis; authors must reconcile inference/formatting differences with the manuscript.

## B. Model execution (organized and syntax-checked, not GPU-tested during packaging)

1. Follow DATA_SETUP and run preflight on the private input folder. Keep published CSVs immutable.
2. In each notebook run installation, **Restart session**, then the configuration cell. Set DATA_ROOT and RUN_DIR consistently. Installing packages alone does not stage audio or checkpoints.
3. Main notebook: logical Cells 2–6 prepare paths/holdout/models/scoring and perform the reproduction check. It must pass. Continue Cells 7, 8, 9, 10, 12 and 13. The separate historical E9 repair cell is archived, not in the clean sequence. VCTK can be done another day after reinitializing setup. Saved rows are skipped according to existing keys.
4. Timing notebook: use a new runtime on a different day. Run setup and warmup, then logical Cell 11 and completeness/export. A runtime-local unique session ID prevents rerunning the same timing cell from appending duplicate completed keys. A new runtime creates a new session. The archived timing CSV records two historical sessions; new sessions go into RUN_DIR and do not alter it. No scoring models are needed for this notebook.
5. Extra-run notebook: install/restart/configure; Cells 2–6; EXTRA RUN. It produces 120 rows and a run-ID metadata file. Export now follows the current RESULTS_PATH instead of a historical filename. Resume in the same runtime retains the run ID; after runtime loss, explicitly recover the matching run ID/path if resuming rather than starting another run.
6. YourTTS: A1, restart, configure, A2 and A3. Then a fresh runtime: B1, restart, configure the SAME DATA_ROOT/RUN_DIR, B2–B5. The filename is unchanged; the executed original contains both sessions' outputs under archive/revision_executed.

Do not use historical notebooks/template as extra revision steps. Their outputs support provenance and older experiments. Logical Cell labels inside the code, rather than notebook physical positions, are the stable references after cleanup.

Installation cells retain original package pins. Dependency conflicts on current Colab remain a possible unresolved runtime issue; clean-session testing has not been claimed. Main/extra checks require legacy output WAVs that are not published in this package. Stop and inspect an unsuccessful reproduction check; do not loosen its tolerance to obtain a pass.
