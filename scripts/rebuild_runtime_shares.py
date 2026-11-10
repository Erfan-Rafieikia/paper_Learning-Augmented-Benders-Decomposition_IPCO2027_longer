"""Rebuild the author-only IPCO callback-stage time-share table.

Usage:
  python scripts/rebuild_runtime_shares.py ipco_traces_logs.tgz \
    --summary-dir ../coding_Learning-Augmented-Benders-Decomposition_IPCO2027/results/ipco_20261108

The two CSVs in --summary-dir identify the matched run roots and task IDs.
The input archive must contain the original per-run convergence-trace CSVs.
Only p4/p5/p10/p50 at 100/300/500 scenarios (BD solved cases) are included.
"""
import argparse
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd


BD_FILE = 'standard_bd_S100_300_500.csv'
METHOD_FILE = 'labd_rnd_vs_bd_S100_300_500.csv'


def read_trace(archive, files, root, task):
    key = f'/labd_ipco_{root}/task_{int(task)}_'
    found = [m for name, m in files.items() if key in name]
    if len(found) != 1:
        raise ValueError(f'{root}, task {task}: expected one trace, got {len(found)}')
    return pd.read_csv(archive.extractfile(found[0]))


def shares(trace, method):
    starts = trace.loc[trace.event == 'solver_iteration_start',
                       ['iteration', 'elapsed_seconds', 'callback_context']]
    ends = trace.loc[trace.event == 'solver_iteration_end',
                     ['iteration', 'elapsed_seconds', 'callback_context']]
    pairs = starts.merge(ends, on='iteration', suffixes=('_s', '_e'),
                         validate='one_to_one')
    if len(pairs) != len(starts) or len(pairs) != len(ends):
        raise ValueError('Unmatched callback start/end event')
    if not (pairs.callback_context_s == pairs.callback_context_e).all():
        raise ValueError('Mismatched callback contexts')
    durations = (pairs.elapsed_seconds_e - pairs.elapsed_seconds_s).clip(lower=0)
    warm_mask = (pairs.iteration <= 5) if method == 'LABD' else np.zeros(len(pairs), dtype=bool)
    warm = float(durations[warm_mask].sum())
    mip = float(durations[(~warm_mask) & (pairs.callback_context_s == 'MIPSOL')].sum())
    node = float(durations[(~warm_mask) & (pairs.callback_context_s == 'MIPNODE')].sum())
    total = float(trace.elapsed_seconds.iloc[-1])
    other = total - warm - mip - node
    if other < -1e-5 or total <= 0:
        raise ValueError('Invalid time decomposition')
    return [100 * x / total for x in (warm, mip, node, other)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive')
    p.add_argument('--summary-dir', required=True)
    p.add_argument('--output', default='time_share_audit.csv')
    args = p.parse_args()
    summary = Path(args.summary_dir)
    bd = pd.read_csv(summary / BD_FILE)
    methods = pd.read_csv(summary / METHOD_FILE)
    bd['M'] = 'BD'
    bd['share'] = 0
    selected = set(zip(bd.loc[bd.stopping_reason == 'OPTIMAL', 'inst'],
                       bd.loc[bd.stopping_reason == 'OPTIMAL', 'S']))
    runs = pd.concat([bd, methods], ignore_index=True)
    runs = runs[[((r.inst, r.S) in selected) for r in runs.itertuples()]].copy()
    assert len(runs) == 84, f'Expected 84 matched runs, found {len(runs)}'

    audit = []
    with tarfile.open(args.archive, 'r:gz') as archive:
        files = {m.name: m for m in archive.getmembers()
                 if m.isfile() and m.name.endswith('.csv')}
        for r in runs.itertuples():
            values = shares(read_trace(archive, files, r.root, r.task), r.M)
            audit.append({'method': r.M, 'share': int(r.share),
                          'instance': r.inst, 'scenarios': r.S,
                          'solution_time_sec': float(r.solution_time_sec),
                          **dict(zip(('warmup_pct', 'integer_pct', 'lp_node_pct',
                                      'other_pct'), values))})
    df = pd.DataFrame(audit)
    df.to_csv(args.output, index=False)
    grouped = df.groupby(['method', 'share'], sort=True)
    display = grouped[['warmup_pct', 'integer_pct', 'lp_node_pct',
                       'other_pct']].mean().round(1)
    display.insert(0, 'median_time_s', grouped.solution_time_sec.median().round(1))
    print(display.to_string())
    print(f'Wrote {len(df)} run-level audit records to {args.output}')


if __name__ == '__main__':
    main()
