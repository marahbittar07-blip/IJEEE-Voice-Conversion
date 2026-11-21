#!/usr/bin/env python3
"""Prepare runtime data from the authors' local ZIP exports, never into the repo.
Does not download, infer missing recordings, modify scientific CSVs, or convert audio.
"""
import argparse,csv,io,json,shutil,zipfile
from pathlib import Path,PurePosixPath

def copy_members(archive,dest,predicate):
    count=0
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            parts=PurePosixPath(info.filename).parts
            if info.is_dir() or '..' in parts or PurePosixPath(info.filename).is_absolute():continue
            if not predicate(parts):continue
            target=dest.joinpath(*parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            data=z.read(info)
            if target.exists() and target.read_bytes()!=data:
                raise ValueError(f'Refusing to replace a different file: {target}')
            target.write_bytes(data);count+=1
    return count

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--selected',type=Path,required=True,help='selected_hybrid_data ZIP')
    p.add_argument('--eval',type=Path,required=True,help='kathleen_independent_refs ZIP')
    p.add_argument('--holdout10',type=Path,required=True)
    p.add_argument('--holdout40',type=Path,required=True)
    p.add_argument('--legacy',type=Path,required=True,help='final_hybrid_comparison ZIP with historical WAVs')
    p.add_argument('--models',type=Path,required=True,help='local models ZIP, not published with repository')
    p.add_argument('--joe',type=Path,required=True,help='joe.tar.gz downloaded from original corpus')
    a=p.parse_args();dest=a.data_root.resolve();repo=Path(__file__).resolve().parents[1]
    if dest==repo or repo in dest.parents:raise ValueError('Runtime audio/models must live outside the public repo')
    sources=[(a.selected,'selected_hybrid_data'),(a.eval,'kathleen_independent_refs'),(a.holdout10,'final_holdout_data'),(a.holdout40,'final_holdout_data_40'),(a.legacy,'final_hybrid_comparison')]
    for archive,folder in sources:
        count=copy_members(archive,dest,lambda parts:len(parts)>1 and parts[0]==folder and Path(parts[-1]).suffix.lower() in ['.wav','.csv','.json'])
        if not count:raise ValueError(f'Expected folder {folder}/ missing in {archive}')
        print(folder,count,'files')
    count=copy_members(a.models,dest,lambda parts:'/'.join(parts) in ['models/OpenVoiceV2/converter/config.json','models/OpenVoiceV2/converter/checkpoint.pth'])
    if count!=2:raise ValueError('Expected converter config and checkpoint in models ZIP')
    dest.mkdir(parents=True,exist_ok=True);joe_target=dest/'joe.tar.gz'
    if a.joe.resolve()!=joe_target:
        if joe_target.exists():raise ValueError('joe.tar.gz already exists; use it directly as --joe to avoid replacement')
        shutil.copy2(a.joe,joe_target)
    # Rebase only runtime copies of metadata paths, never archived repository data.
    for folder,filename in [('final_holdout_data','holdout_metadata.csv'),('final_holdout_data_40','holdout40_metadata.csv')]:
        path=dest/folder/filename
        with path.open(newline='',encoding='utf-8-sig') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
        for row in rows:
            row['prepared_wav']=str(dest/folder/Path(row['prepared_wav']).name)
            if not Path(row['prepared_wav']).is_file():raise ValueError(f'Missing audio for {row["sample"]}')
        with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print('Prepared runtime copies. Run preflight_inputs.py before opening Colab. This is data staging, not a model rerun.')
if __name__=='__main__':main()
