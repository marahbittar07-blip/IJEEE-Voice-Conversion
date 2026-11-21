#!/usr/bin/env python3
"""Check the input file layout without loading PyTorch or any model."""
import argparse,csv,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data-root',type=Path,required=True);args=ap.parse_args();r=args.data_root.resolve()
    needed=['joe.tar.gz','final_holdout_data/holdout_metadata.csv','final_holdout_data_40/holdout40_metadata.csv','models/OpenVoiceV2/converter/config.json','models/OpenVoiceV2/converter/checkpoint.pth']
    needed += [f'selected_hybrid_data/joe_source_{i:02d}.wav' for i in range(1,4)]
    needed += ['selected_hybrid_data/kathleen_reference.wav']+[f'selected_hybrid_data/kathleen_conditioning_ref_{i:02d}.wav' for i in [2,3]]
    needed += [f'kathleen_independent_refs/kathleen_eval_{i:02d}.wav' for i in range(1,11)]
    patterns=['seed_based_outputs/optimized_hybrid/optimized_hybrid_sample_{:02d}_tau_0.5_steps_10.wav','seed_based_outputs/default_hybrid/default_hybrid_sample_{:02d}_tau_0.3_steps_20.wav','seed_based_outputs/seed_only/seed_only_sample_{:02d}_steps_10.wav','openvoice_outputs/tau_0.5/openvoice_sample_{:02d}_tau_0.5.wav']
    needed += ['final_hybrid_comparison/'+p.format(i) for p in patterns for i in range(1,11)]
    missing=[str(r/x) for x in needed if not (r/x).is_file()]
    for folder,name,count in [('final_holdout_data','holdout_metadata.csv',10),('final_holdout_data_40','holdout40_metadata.csv',40)]:
        meta=r/folder/name
        if not meta.is_file():continue
        with meta.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
        if len(rows)!=count or {int(x['sample']) for x in rows}!=set(range(1,count+1)):missing.append(f'INVALID metadata count/IDs: {meta}')
        for row in rows:
            if not Path(row['prepared_wav']).is_file():missing.append('Unresolved prepared_wav: '+row['prepared_wav'])
    if missing:
        print('\n'.join(missing));raise SystemExit('Input check FAILED; do not start inference.')
    print('Input file layout PASS. Audio/weight identity and GPU/runtime execution are separate checks.')
if __name__=='__main__':main()
