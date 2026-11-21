#!/usr/bin/env python3
"""Deterministic CPU analysis of archived results, not a model rerun.

Table V is independently reconstructed with declared settings, not claimed to
be the unavailable original statistics script. Graphs are new renderings.
"""
import argparse,json,hashlib,platform
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy.stats import wilcoxon

METRICS=['sim_ecapa_cond','sim_ecapa_eval','sim_wavlm_eval','wer_large','cer_large','utmos','latency','latency_e2e','rtf']
def read(path,keys,rows):
    d=pd.read_csv(path)
    if len(d)!=rows or d.duplicated(keys).any():
        raise ValueError(f'Unexpected count or duplicate keys: {path}')
    return d

def summarize(d,by,columns):
    return d.groupby(by,dropna=False)[columns].agg(['mean','std','count'])

def save(d,p):
    if isinstance(d.columns,pd.MultiIndex):d.columns=['_'.join(c) for c in d.columns]
    d.to_csv(p)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--out',type=Path)
    ap.add_argument('--seed',type=int,default=20261119)
    ap.add_argument('--resamples',type=int,default=20000)
    args=ap.parse_args();root=args.repo.resolve();out=(args.out or root/'analysis_outputs').resolve()
    if args.resamples<1000:raise ValueError('Use at least 1000 resamples')
    # Input archives are immutable. Output may not overlap any input directory.
    for part in ['results','data','archive','notebooks','configs']:
        if out==root/part or (root/part) in out.parents:raise ValueError('Output overlaps archived inputs')
    out.mkdir(parents=True,exist_ok=True);r=root/'results/revision';yt=root/'results/yourtts'
    h=read(r/'E9_holdout40.csv',['system','sample'],280)
    g=read(r/'E8_grid_5x5_seeds.csv',['tau','steps','sample','seed_set'],375)
    extras=sorted(r.glob('E14_extra_*.csv'))
    if len(extras)!=1:raise ValueError('Expected exactly one archived E14 input')
    e=read(extras[0],['system','sample'],120)
    y=read(yt/'E15_yourtts_holdout40.csv',['system','sample'],40)
    a=read(r/'E10_extra_refs.csv',['reference','system','sample'],240)
    t=read(r/'E11_session_timing.csv',['session','system','sample'],80)
    v=read(r/'E12_vctk_pairs.csv',['pair','system','sample'],150)
    for d in [h,e,y,a]:
        by=['reference','system'] if d is a else ['system']
        for _,b in d.groupby(by):
            if len(b)!=40 or set(b['sample'])!=set(range(1,41)):raise ValueError('Incomplete holdout group')
    assert g.groupby(['tau','steps']).size().eq(15).all()
    assert g.groupby(['tau','steps']).ngroups==25
    assert t.groupby(['session','system']).size().eq(10).all() and t.session.nunique()==2
    assert v.groupby(['pair','system']).size().eq(10).all()
    selected_name='OpenVoice-SeedVC (tau 0.1, 10 steps)'
    reference='Reference cascade (tau 0.3, 20)'
    # Table I common protocol: four main paths + YourTTS + reverse reference.
    names=['OpenVoice V2 (tau 0.5)','Seed-VC (10 steps)','Seed-VC (25 steps, default)',reference]
    one=pd.concat([h[h.system.isin(names)],y,e[e.system=='SeedVC-OpenVoice (tau 0.3, 20 steps)']])
    save(summarize(one,'system',METRICS),out/'table_I.csv')
    g['rtf']=g.latency/g.src_duration
    grid=g.pivot_table(index='steps',columns='tau',values='sim_ecapa_cond')
    grid.to_csv(out/'table_II.csv')
    for key,stage in [('steps','t_seedvc'),('tau','t_openvoice')]:
        save(summarize(g,key,['sim_ecapa_cond','wer_large','utmos',stage,'latency','rtf']),out/f'table_III_by_{key}.csv')
    four=pd.concat([h,e[e.system==selected_name]])
    save(summarize(four,'system',METRICS),out/'table_IV.csv')
    ranked=g.groupby(['tau','steps']).agg(sim=('sim_ecapa_cond','mean'),sd=('sim_ecapa_cond','std'),wer=('wer_large','mean'))
    best=ranked.sim.idxmax();threshold=float(ranked.loc[best,'sim']-ranked.loc[best,'sd'])
    eligible=ranked[ranked.sim>=threshold].reset_index().sort_values(['steps','wer','sim'],ascending=[True,True,False])
    choice=eligible.iloc[0]
    if (choice.tau,int(choice.steps))!=(0.1,10):raise ValueError('Selection differs from R10')
    eligible.to_csv(out/'selection_eligible.csv',index=False)
    sel=e[e.system==selected_name].set_index('sample').sort_index()
    comparisons=[(reference,['sim_ecapa_cond','sim_ecapa_eval','sim_wavlm_eval','wer_large','cer_large','utmos','latency']),
      ('Seed-VC (10 steps)',['sim_ecapa_cond','sim_ecapa_eval','sim_wavlm_eval','wer_large','latency']),
      ('Seed-VC (25 steps, default)',['sim_ecapa_eval','wer_large','latency']),
      ('Selected cascade (tau 0.5, 10)',['sim_ecapa_cond','wer_large','latency'])]
    paired=[]
    for system,metrics in comparisons:
        base=h[h.system==system].set_index('sample').sort_index()
        for metric in metrics:
            diff=(sel[metric]-base[metric]).to_numpy()
            if not np.isfinite(diff).all():raise ValueError('Invalid paired differences')
            # A separate seeded RNG per contrast gives stable results if contrast order changes.
            offset=int.from_bytes(hashlib.sha256((system+'|'+metric).encode()).digest()[:4],'little')
            rng=np.random.default_rng(np.random.SeedSequence([args.seed,offset]))
            boot=diff[rng.integers(0,len(diff),size=(args.resamples,len(diff)))].mean(axis=1)
            lo95,lo90,hi90,hi95=np.quantile(boot,[.025,.05,.95,.975])
            p=1.0 if np.all(diff==0) else float(wilcoxon(diff,zero_method='wilcox',correction=False,alternative='two-sided',method='auto').pvalue)
            margin=.03 if metric in ['sim_ecapa_cond','sim_ecapa_eval','sim_wavlm_eval'] else .05 if metric in ['wer_large','cer_large'] else np.nan
            assess=system in [reference,'Selected cascade (tau 0.5, 10)'] and np.isfinite(margin)
            paired.append(dict(comparison=system,metric=metric,mean_difference=diff.mean(),ci95_low=lo95,ci95_high=hi95,ci90_low=lo90,ci90_high=hi90,p_wilcoxon=p,lower=int((diff<0).sum()),higher=int((diff>0).sum()),margin=margin if assess else np.nan,within_margin=bool(lo90>-margin and hi90<margin) if assess else None))
    pd.DataFrame(paired).to_csv(out/'table_V_reconstructed.csv',index=False)
    save(summarize(t,['session','system'],['latency','latency_e2e']),out/'table_VI_sessions.csv')
    save(summarize(a,['reference','system'],['sim_ecapa_cond','sim_ecapa_eval','wer_large','utmos']),out/'table_VI_references.csv')
    save(summarize(e[e.order=='sv_ov'],'system',METRICS),out/'table_VI_reverse.csv')
    save(summarize(v,'system',['sim_ecapa_cond','sim_ecapa_eval','wer_large','utmos','latency']),out/'table_VI_vctk.csv')
    save(summarize(v,['pair','system'],['sim_ecapa_cond','sim_ecapa_eval','wer_large','utmos','latency']),out/'vctk_per_pair.csv')
    # New visualizations, not replicas of the embedded manuscript graphics.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for filename,data in [('paths_tradeoff',one),('holdout_latency_similarity',four)]:
        means=data.groupby('system').mean(numeric_only=True)
        fig,ax=plt.subplots(figsize=(9,6))
        for name,b in means.iterrows():
            xx=b.sim_ecapa_eval if filename=='paths_tradeoff' else b.latency
            yy=b.wer_large if filename=='paths_tradeoff' else b.sim_ecapa_eval
            ax.scatter(xx,yy);ax.annotate(name,(xx,yy),xytext=(4,4),textcoords='offset points',fontsize=7)
        ax.set_xlabel('Independent ECAPA similarity' if filename=='paths_tradeoff' else 'Latency (s)')
        ax.set_ylabel('Mean sentence WER (Whisper-large-v3)' if filename=='paths_tradeoff' else 'Independent ECAPA similarity')
        if filename=='paths_tradeoff':ax.invert_yaxis()
        ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/f'{filename}.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,4))
    for tau,b in g.groupby('tau'):
        s=b.groupby('steps').mean(numeric_only=True)
        axs[0].plot(s.index,s.sim_ecapa_cond,'o-',label=f'tau={tau}')
        axs[1].plot(s.index,s.wer_large,'o-',label=f'tau={tau}')
    axs[0].axhline(threshold,color='gray',ls='--');axs[0].set_ylabel('Conditioning ECAPA similarity');axs[1].set_ylabel('Mean sentence WER')
    for ax in axs:ax.set_xlabel('Diffusion steps');ax.grid(alpha=.2)
    axs[1].legend();fig.tight_layout();fig.savefig(out/'tuning_grid.png',dpi=180);plt.close(fig)
    ref=h[h.system==reference].latency.mean();selected=sel.latency.mean()
    inputs=sorted(list(r.glob('*.csv'))+list(yt.glob('*.csv')))
    manifest=dict(seed=args.seed,resamples=args.resamples,python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__,wilcoxon=dict(zero_method='wilcox',correction=False,alternative='two-sided',method='auto'),selection=dict(tau=float(choice.tau),steps=int(choice.steps),similarity_threshold=threshold),latency_saving_percent=100*(ref-selected)/ref,inputs={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},status='Independent CPU reconstruction; original bootstrap seed/options unavailable. Figures are new renderings; no audio/model rerun.')
    (out/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2))
    (out/'README.md').write_text('# Analysis outputs\n\nGenerated from immutable archived CSVs using scripts/analyze_results.py. Means/SDs and selection are recomputed. Table V is an independently reconstructed analysis with settings in analysis_manifest.json; it is not the unavailable original analysis script. Its CI endpoints and some p-value rounding can differ from R10. These require author review before resubmission. Plots are new visualizations, not pixel-identical manuscript figures. WER is mean per-sentence WER, not pooled corpus WER.\n')
    print(f'PASS: validated input counts/keys, selected tau=0.1/10 steps; latency saving {manifest["latency_saving_percent"]:.2f}%; outputs: {out}')
if __name__=='__main__':main()
