# Main notebook changes (19 November 2026)

The exact previous notebook, including historical outputs, is preserved under `archive/revision_executed/01_Revision_Main_Experiments.ipynb`.

Execution copy: `notebooks/01_Revision_Main_Experiments.ipynb`.

- Kept original physical code cells 4, 5, 6, 8, 10, 12, 14, 16, 17, 20, 22, 23, 24, 27, in that order. Added an introductory Markdown cell. Logical code Cell labels remain unchanged.
- Removed connection/version probes, blanks, early export, old E9 repair and the p232 length diagnostic from the execution flow. These remain in the archived original.
- Cleared saved outputs from the execution copy; originals retain them.
- E9 initializes latency_e2e for every system, including standalone models, so all 280 rows share one schema. Non-cascades store an empty value (NaN).
- append_row checks schema/column order, rejects malformed existing CSVs, writes a complete temporary file, flushes, and replaces the target atomically. It supports interrupted single-writer resumption; it is not a concurrent multi-writer database. CSV writing is outside conversion timing.
- No changes to model loading, inference, seeds, precision, speaker references, timing functions, grid settings, scoring, VCTK fallback or archived result files.

Validation: Python syntax parsed for each execution cell; writer tested locally on synthetic mixed-system/transcript data, including a 280-row fixture, permuted incoming column order, and rejection without modification of an invalid schema/malformed existing row. No model conversion or GPU run was performed. Dependency compatibility, dataset provisioning, legacy-output prerequisites and complete reproduction remain open.

Next work: prepare clean copies of the timing/extra-run notebooks and build the deterministic analysis script. The YourTTS executed notebook remains unchanged.


Current status supersedes earlier next-work notes: see RELEASE_STATUS.md. All four organized copies are now supplied; independent CPU analysis is included. Full GPU/public-data reproduction is still unverified.
