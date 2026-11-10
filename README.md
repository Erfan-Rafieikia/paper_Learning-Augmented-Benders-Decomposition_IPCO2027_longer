# paper_Learning-Augmented-Benders-Decomposition_IPCO2027_longer

Copy of the IPCO 2027 submission draft (from `paper_Learning-Augmented-Benders-Decomposition_IPCO2027`,
commit 3f92201) with an extra appendix of background material for discussions with coauthors:
Gurobi settings, data generation, run statistics and diagnostic figures.

This version is NOT for submission. The submission repo is the shorter one.

Build: `latexmk -pdf main.tex`

The author-only `meeting-appendix.tex` now contains the combined methods, Gurobi-log, 500-scenario master-bound trajectories, search diagnostics, and objective-guard audit. The five bound figures are generated directly with PGFPlots from `figures/bounds_{p4,p5,p10,p20,p50}_500.csv` through `figures/master-bound-plots.tex`, so no external plotting step is needed. Each instance now has one full-run plot with elapsed seconds on a base-10 logarithmic horizontal axis and Gurobi master objective values on a linear vertical axis; solid lines are master upper bounds and dashed lines are master lower bounds. The logarithmic scale reveals early bound changes without a separate zoom panel. The inexact methods' bounds refer to their surrogate masters, not the original objective.

## Reproducing the discussion diagnostics

The original Gurobi text log is **not** the plotting source. The callback reads
Gurobi's runtime, objective bound and incumbent values and records them in
`convergence_traces/*.csv`. `figures/bounds_*_500.csv` contains extracted
coordinates of those observed Gurobi master bounds.

From the longer-paper repository root, with the original trace archive:

```bash
python -m pip install pandas numpy
python scripts/rebuild_master_bounds.py /path/to/ipco_traces_logs.tgz
latexmk -pdf main.tex
```

The first script recreates all five figure-coordinate CSVs. LaTeX uses a
**logarithmic x-axis (elapsed seconds)** and a linear objective y-axis.

For the callback-stage timing audit, clone the IPCO coding repository
alongside this one. Its `results/ipco_20261108` directory contains the
matched 100/300/500-scenario summary CSVs. Then run:

```bash
python scripts/rebuild_runtime_shares.py /path/to/ipco_traces_logs.tgz \
  --summary-dir ../coding_Learning-Augmented-Benders-Decomposition_IPCO2027/results/ipco_20261108
```

The output is a run-level `time_share_audit.csv` and grouped percentages.
These percentages separate the first five LABD cut-generation rounds,
subsequent integer-candidate and LP-node cut-generation rounds, and all
remaining Gurobi elapsed time. They do **not** separately identify exact-LP
solution, prediction, selection, and certification costs; those require the
full per-run `solution_log.xlsx` profiler fields.
