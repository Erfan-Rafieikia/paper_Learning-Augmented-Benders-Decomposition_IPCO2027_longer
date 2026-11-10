# paper_Learning-Augmented-Benders-Decomposition_IPCO2027_longer

Copy of the IPCO 2027 submission draft (from `paper_Learning-Augmented-Benders-Decomposition_IPCO2027`,
commit 3f92201) with an extra appendix of background material for discussions with coauthors:
Gurobi settings, data generation, run statistics and diagnostic figures.

This version is NOT for submission. The submission repo is the shorter one.

Build: `latexmk -pdf main.tex`

The author-only `meeting-appendix.tex` now contains the combined methods, Gurobi-log, 500-scenario master-bound trajectories, search diagnostics, and objective-guard audit. The five bound figures are generated directly with PGFPlots from `figures/bounds_{p4,p5,p10,p20,p50}_500.csv` through `figures/master-bound-plots.tex`, so no external plotting step is needed. Each instance now has one full-run plot with elapsed seconds on a base-10 logarithmic horizontal axis and Gurobi master objective values on a linear vertical axis; solid lines are master upper bounds and dashed lines are master lower bounds. The logarithmic scale reveals early bound changes without a separate zoom panel. The inexact methods' bounds refer to their surrogate masters, not the original objective.
