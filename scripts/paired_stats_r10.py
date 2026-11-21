"""Exact script behind the statistics reported in manuscript R10 (Tables I-VI, including Table V).

Usage:  python scripts/paired_stats_r10.py         (run from the repository root)
Writes: analysis_outputs/r10_exact/*.csv
This is the script that produced the R10 numbers (bootstrap generator seed 2026). scripts/analyze_results.py is an
independent reconstruction with a different seed; both give identical means, SDs and p-values.

Conventions
* Paired design: every comparison is on the same holdout sentences, with the same seeds.
* Bootstrap: 20,000 resamples of the paired differences, fixed generator seed 2026.
* Wilcoxon signed-rank test (scipy, method "auto": exact when n <= 50 and there are no ties or zeros).
* Equivalence (TOST): declared when the 90% bootstrap interval lies inside the margin
  (+/-0.03 for speaker similarity, +/-0.05 for WER and CER).
* Selection rule (Section IV-D): (i) keep settings whose mean similarity is within one SD of the best setting,
  where the SD is taken over all utterance-seed observations of the best setting; (ii) choose the lowest
  computational cost (the Seed-VC step count, because tau does not change the computation); (iii) break ties
  by lowest WER, then highest similarity.
"""
import glob, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

RV = os.path.join("results", "revision"); YT = os.path.join("results", "yourtts"); O = os.path.join("analysis_outputs", "r10_exact"); os.makedirs(O, exist_ok=True)
B, SEED = 20000, 2026
MARGIN = {"sim_ecapa_cond": 0.03, "sim_ecapa_eval": 0.03, "sim_wavlm_eval": 0.03, "wer_large": 0.05, "cer_large": 0.05}
METRICS = ["sim_ecapa_cond", "sim_ecapa_eval", "sim_wavlm_eval", "leak_ecapa_source", "wer_large", "cer_large",
           "wer_small", "utmos", "latency", "latency_e2e", "rtf"]

# ---------- holdout: 40 sentences, all systems ----------
h = pd.read_csv(os.path.join(RV, "E9_holdout40.csv"))
parts = [h]
for f in sorted(glob.glob(os.path.join(RV, "E14_extra_*.csv"))):
    parts.append(pd.read_csv(f)[[c for c in h.columns if c in pd.read_csv(f).columns]])
if os.path.exists(os.path.join(YT, "E15_yourtts_holdout40.csv")):
    y = pd.read_csv(os.path.join(YT, "E15_yourtts_holdout40.csv")); parts.append(y[[c for c in h.columns if c in y.columns]])
H = pd.concat(parts, ignore_index=True)
NAMES = {"OpenVoice-SeedVC (tau 0.1, 10 steps)": "Selected cascade (tau 0.1, 10)",
         "Selected cascade (tau 0.5, 10)": "Cascade (tau 0.5, 10)",
         "SeedVC-OpenVoice (tau 0.3, 20 steps)": "Seed-OpenVoice (tau 0.3, 20)",
         "SeedVC-OpenVoice (tau 0.5, 10 steps)": "Seed-OpenVoice (tau 0.5, 10)"}
H["system"] = H["system"].replace(NAMES)
assert H.groupby("system").size().eq(40).all(), H.groupby("system").size()
summ = H.groupby("system")[[m for m in METRICS if m in H.columns]].agg(["mean", "std"]).round(4)
summ.columns = [f"{a}_{b}" for a, b in summ.columns]
summ.sort_values("latency_mean").to_csv(os.path.join(O, "holdout40_summary.csv"))

def paired(df, a, b, col, key="sample"):
    A = df[df.system == a].set_index(key)[col]; Bv = df[df.system == b].set_index(key)[col]
    d = (A - Bv).dropna(); n = len(d)
    rng = np.random.default_rng(SEED)
    bs = d.values[rng.integers(0, n, size=(B, n))].mean(axis=1)
    p = wilcoxon(d).pvalue if (d != 0).any() else 1.0
    lo90, hi90 = np.percentile(bs, [5, 95]); m = MARGIN.get(col)
    return dict(a=a, b=b, metric=col, n=n, mean_diff=d.mean(), ci95_lo=np.percentile(bs, 2.5), ci95_hi=np.percentile(bs, 97.5),
                ci90_lo=lo90, ci90_hi=hi90, wilcoxon_p=p, n_lower=int((d < 0).sum()), n_higher=int((d > 0).sum()),
                margin=m if m else np.nan, equivalent=(bool(-m < lo90 and hi90 < m) if m else np.nan))

SEL, REF = "Selected cascade (tau 0.1, 10)", "Reference cascade (tau 0.3, 20)"
PAIRS = [(SEL, REF), (SEL, "Seed-VC (10 steps)"), (SEL, "Seed-VC (25 steps, default)"), (SEL, "Cascade (tau 0.5, 10)"),
         (SEL, "Cascade (tau 0.3, 10)"), ("Cascade (tau 0.5, 20)", REF),
         ("Seed-OpenVoice (tau 0.5, 10)", "Seed-OpenVoice (tau 0.3, 20)"), ("Seed-OpenVoice (tau 0.5, 10)", "Seed-VC (10 steps)"),
         ("Seed-OpenVoice (tau 0.3, 20)", REF), ("Seed-OpenVoice (tau 0.5, 10)", SEL)]
if "YourTTS (ASR-mediated)" in set(H.system):
    PAIRS += [("YourTTS (ASR-mediated)", "Seed-VC (10 steps)"), ("YourTTS (ASR-mediated)", SEL)]
cols = ["sim_ecapa_cond", "sim_ecapa_eval", "sim_wavlm_eval", "wer_large", "cer_large", "utmos", "latency"]
pd.DataFrame([paired(H, a, b, c) for a, b in PAIRS for c in cols]).round(4).to_csv(os.path.join(O, "holdout40_paired_tests.csv"), index=False)

# ---------- tuning grid: 5 tau x 5 steps x 3 utterances x 5 seeds ----------
g = pd.read_csv(os.path.join(RV, "E8_grid_5x5_seeds.csv"))
G = g.groupby(["tau", "steps"]).agg(sim=("sim_ecapa_cond", "mean"), sim_sd=("sim_ecapa_cond", "std"), wer_large=("wer_large", "mean"),
                                    wer_small=("wer_small", "mean"), utmos=("utmos", "mean"), latency=("latency", "mean"),
                                    t_openvoice=("t_openvoice", "mean"), t_seedvc=("t_seedvc", "mean"), n=("sim_ecapa_cond", "size")).reset_index()
best = G.loc[G.sim.idxmax()]; thr = best.sim - best.sim_sd
G["in_band"] = G.sim >= thr
cand = G[G.in_band]; cand = cand[cand.steps == cand.steps.min()]
pick = cand.sort_values(["wer_large", "sim"], ascending=[True, False]).iloc[0]
G["selected"] = (G.tau == pick.tau) & (G.steps == pick.steps)
G.round(4).to_csv(os.path.join(O, "grid_selection.csv"), index=False)
print(f"Grid rule: best tau={best.tau} steps={int(best.steps)} sim={best.sim:.4f}, band >= {thr:.4f}; selected tau={pick.tau}, steps={int(pick.steps)}")

# ---------- timing across sessions ----------
s = pd.read_csv(os.path.join(RV, "E11_session_timing.csv"))
s.groupby(["session", "system"])[["latency", "latency_e2e"]].agg(["mean", "std"]).round(4).to_csv(os.path.join(O, "timing_sessions.csv"))

# ---------- extra target references ----------
e10 = pd.read_csv(os.path.join(RV, "E10_extra_refs.csv"))
e10.groupby(["reference", "system"])[["sim_ecapa_cond", "sim_ecapa_eval", "sim_wavlm_eval", "wer_large", "utmos"]].mean().round(4)\
   .to_csv(os.path.join(O, "extra_references_summary.csv"))

# ---------- VCTK pairs ----------
v = pd.read_csv(os.path.join(RV, "E12_vctk_pairs.csv"))
v.groupby(["pair", "system"])[["sim_ecapa_cond", "sim_ecapa_eval", "sim_wavlm_eval", "leak_ecapa_source", "wer_large", "cer_large", "utmos", "latency", "rtf"]]\
 .mean().round(4).to_csv(os.path.join(O, "vctk_summary.csv"))
v["key"] = v.pair + "_" + v["sample"].astype(str)
VS = "Selected cascade (tau 0.5, 10)"            # VCTK was run before the 5-seed grid moved the pick to tau = 0.1
vp = [paired(v, VS, b, c, key="key") for b in ["Reference cascade (tau 0.3, 20)", "Seed-VC (10 steps)", "Seed-VC (25 steps, default)"]
      for c in ["sim_ecapa_cond", "sim_ecapa_eval", "wer_large", "utmos", "latency"]]
pd.DataFrame(vp).round(4).to_csv(os.path.join(O, "vctk_paired_tests.csv"), index=False)

# ---------- anchors ----------
a7 = pd.read_csv(os.path.join(RV, "E7_anchors.csv")); a12 = pd.read_csv(os.path.join(RV, "E12_vctk_anchors.csv"))
a7.assign(pair="joe->kathleen").groupby(["pair", "anchor"])[["sim_ecapa", "sim_wavlm"]].agg(["mean", "std"]).round(4).to_csv(os.path.join(O, "anchors_main_pair.csv"))
a12.groupby(["pair", "anchor"])[["sim_ecapa", "sim_wavlm"]].agg(["mean", "std"]).round(4).to_csv(os.path.join(O, "anchors_vctk.csv"))
print("Wrote:", sorted(os.listdir(O)))
