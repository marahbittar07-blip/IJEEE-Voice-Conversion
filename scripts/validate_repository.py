#!/usr/bin/env python3
"""CPU-only structural checks; never asserts GPU reproduction."""
import ast,csv,hashlib,json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    expected={'E8_grid_5x5_seeds.csv':375,'E9_holdout40.csv':280,'E10_extra_refs.csv':240,'E11_session_timing.csv':80,'E12_vctk_pairs.csv':150,'E14_extra_20261116_202913_17be5126.csv':120}
    for name,n in expected.items():
        with (root/'results/revision'/name).open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
        assert len(rows)==n,(name,len(rows),n)
    for p in (root/'scripts').glob('*.py'):ast.parse(p.read_text())
    for p in (root/'notebooks').glob('*.ipynb'):
        b=json.loads(p.read_text())
        for c in b['cells']:
            if c['cell_type']=='code':ast.parse(''.join(c['source']));assert not c['outputs']
        assert (root/'archive/revision_executed'/p.name).exists()
    with (root/'data/file_ids.csv').open(newline='',encoding='utf-8-sig') as f:ids=list(csv.DictReader(f))
    assert not any('TO_BE_FILLED' in str(row) for row in ids)
    def meta(n):
        with (root/'data'/n).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
    a,b=meta('holdout_metadata.csv'),meta('holdout40_metadata.csv')
    assert len(a)==10 and len(b)==40
    assert [(x['original_id'],x['transcript']) for x in a]==[(x['original_id'],x['transcript']) for x in b[:10]]
    assert not any(p.suffix.lower() in ['.wav','.pth','.pt','.webm','.flac'] for p in root.rglob('*') if p.is_file())
    print('PASS: notebook/script syntax, cleared execution outputs, archived originals, result counts, metadata IDs/text, no audio/weights. GPU/dependencies not tested.')
if __name__=='__main__':main()
