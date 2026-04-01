# Strategy Whitepaper

## Current Date
April 1, 2026

## Deadline Assumption
April 30, 2026 — last calendar day of the competition month (S6E4 default assumption).

## Days Remaining
29

## Read

This is the opening of week 1. Zero scientist runs, zero analyst sessions, zero submissions. There is no CV anchor, no leaderboard signal, and no analyst knowledge yet. Coverage is entirely blank across all lanes: preprocessing, features, models, ensembles, and moonshots.

The human directive is clear and aligns well with the lifecycle default for the opening stage: invest heavily in EDA and establish a diverse set of base models. Ensembling is explicitly deferred. With 29 days available, there is no pressure to compress; the right posture is to build a wide, solid foundation before any narrowing begins.

The lifecycle guide's Opening emphasis (EDA 70 / Base Models 25 / Refinement 5 / Ensembling 0 / Moonshots 0) is a good match for this moment. The human directive reinforces this by making EDA primary and expanding the base-model mandate beyond the default 25% — a reasonable deviation given that the directive asks for diversity across model families, not just a single anchoring run.

No CV/LB translation data exists. The supervisor should treat the first few submissions as signal-gathering rather than score-chasing: they establish whether local CV tracks LB at all.

## Emphasis

Primary: EDA — establish durable analyst knowledge about the dataset before any model work depends on it. This means class balance, missingness, train/test shift, feature types, outliers, and target-conditional distributions. The analyst should produce findings that the scientist can rely on when designing preprocessing and features.

Secondary: Base Models — once EDA is underway, begin building a diverse model portfolio in parallel. The goal is breadth across model families (linear, tree ensembles, gradient boosted trees, and at least one neural-style option), not depth on any single family. Each base model run should use a clean, minimal preprocessing baseline so results are comparable and the diversity is real.

Background: Preprocessing and Feature Engineering — these should move lightly but not be ignored. The EDA will surface preprocessing requirements (encoding strategy, missing value approach, scaling needs). Basic preprocessing experiments can begin as EDA findings arrive, keeping the scientist productive.

Hold: Ensembling, Moonshots — per human directive, ensembling stays quiet for all of week 1. Moonshots (pseudo-labeling, external data, two-stage pipelines) are not appropriate until a solid base exists. Both lanes should remain on the roadmap but receive no active experiment budget now.

## Guidance For The Supervisor

1. Commission the analyst first. Before any scientist run, ask the analyst to establish a baseline knowledge entry covering: class balance (are High/Low/Medium equally represented?), missingness patterns, feature types (numeric vs. categorical, any boolean-like numerics), train/test distributional shift, and any obvious leakage or data quality flags. This knowledge entry will anchor every preprocessing and feature decision in the coming days.

2. Run a diverse baseline sweep across model families once the analyst's initial findings are in. Prioritise at least four distinct families in the first round: (a) a regularised linear classifier (logistic regression or linear SVM) as the interpretable anchor, (b) a tree ensemble (RandomForest or ExtraTrees), (c) a gradient boosted tree (LightGBM or XGBoost or CatBoost — pick whichever has native categorical support given the feature mix the analyst surfaces), and (d) a HistGradientBoosting run as a near-zero-tuning sanity check. Each run should use the same minimal preprocessing so CV scores are directly comparable.

3. Submit selectively and early to calibrate CV/LB translation. After the first two or three base model runs produce CV scores, pick the best and submit it. The goal is not a leaderboard rank but a data point: does CV correlate with LB? If the gap is large or inverted, flag it immediately and commission an analyst session on fold instability or train/test shift before running more experiments. Submission budget is 5/day; spending one early on a calibration submission is worth it.

## Refresh Triggers

- After the analyst completes the first EDA session and produces a knowledge entry (knowledge will change the preprocessing and feature lane priorities).
- After four or more base model families have a completed CV score (enough to assess coverage and decide whether any family warrants more depth or should be deprioritised).
- After the first LB score arrives and can be compared to the corresponding CV score (CV/LB translation status may shift emphasis significantly).
- If any scientist run surfaces an unexpectedly large CV delta (positive or negative), warranting a lane reprioritisation.
- At the end of week 1 (approximately April 7, 2026), as a scheduled refresh before the build phase begins.
