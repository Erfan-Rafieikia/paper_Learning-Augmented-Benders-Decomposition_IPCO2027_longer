"""Rebuild the five IPCO 500-scenario master-bound plotting CSVs.

Usage:
    python scripts/rebuild_master_bounds.py ipco_traces_logs.tgz

Requires pandas. Run from the longer IPCO paper repository root. The input is the
original convergence-trace archive; no Gurobi solver or Excel is needed.
"""
import argparse
import tarfile
from pathlib import Path

import pandas as pd


BASE = 'labd_ipco_ipco_full_pmedian_20261105_193605'
LABD = 'labd_ipco_ipco_cmp_pmedian_v0_20261106_171133'
INSTANCES = ['p4', 'p5', 'p10', 'p20', 'p50']


def read_trace(archive, members, root, task):
    suffix = f'/{root}/task_{task}_'
    matches = [m for name, m in members.items() if suffix in name]
    if len(matches) != 1:
        raise ValueError(f'Expected one trace for {root}, task {task}; found {len(matches)}')
    return pd.read_csv(archive.extractfile(matches[0]))


def changed_bounds(trace):
    """Keep observations at Gurobi bound changes, initialization and termination."""
    d = (trace[['elapsed_seconds', 'lower_bound', 'master_upper_bound']]
         .rename(columns={'elapsed_seconds': 't', 'lower_bound': 'lb',
                          'master_upper_bound': 'ub'})
         .sort_values('t').drop_duplicates('t').reset_index(drop=True))
    d[['lb', 'ub']] = d[['lb', 'ub']].ffill()
    keep = [0]
    for i in range(1, len(d)):
        old, new = d.iloc[keep[-1]], d.iloc[i]
        changed = any(pd.notna(new[c]) and
                      (pd.isna(old[c]) or abs(new[c] - old[c]) > 1e-7)
                      for c in ['lb', 'ub'])
        if changed or i == len(d) - 1:
            keep.append(i)
    return d.iloc[keep].reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', help='Path to original ipco_traces_logs.tgz')
    ap.add_argument('--out-dir', default='figures', help='Output directory')
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.archive, 'r:gz') as archive:
        members = {m.name: m for m in archive.getmembers()
                   if m.isfile() and m.name.endswith('.csv')}
        for i, instance in enumerate(INSTANCES):
            tasks = {'bd': (BASE, 1 + 7 * i),
                     'labd': (LABD, 1 + 3 * i),
                     'rnd': (BASE, 2 + 7 * i)}
            cols = {}
            for method, (root, task) in tasks.items():
                d = changed_bounds(read_trace(archive, members, root, task))
                for c in ['t', 'lb', 'ub']:
                    cols[f'{c}_{method}'] = d[c]
            path = out / f'bounds_{instance}_500.csv'
            pd.DataFrame(cols).round(2).to_csv(path, index=False, na_rep='nan')
            print(f'{instance}: {path} ({len(pd.DataFrame(cols))} points maximum)')


if __name__ == '__main__':
    main()
