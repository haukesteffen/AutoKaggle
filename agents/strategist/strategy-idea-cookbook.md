# Strategy Idea Cookbook

This file is owned by the strategist role.

It is a reusable bank of strategy ideas for inspiration.

- It does not rank ideas.
- It does not decide timing on its own.
- It should stay broad enough that major areas do not get forgotten.
- When time is abundant, no major area here should remain completely untested.

## Analyst / EDA

- class balance, subgroup balance, missingness, missingness by target
- duplicates, near-duplicates, leakage risk, train/test shift
- fold instability, subgroup instability, error concentration
- high-cardinality columns, rare-category mass, dominant-category mass
- monotonic patterns, outliers, suspiciously clean columns
- target drift by subgroup, target drift by feature buckets
- category overlap between train and test
- feature-type mistakes, boolean-like numerics, numeric-like categoricals

## Validation / Split Ideas

- baseline k-fold, stratified folds, grouped folds, repeated folds
- alternate random seeds for folds
- adversarial validation, train-vs-test classifier
- fold-by-fold diagnostics, per-fold ranking checks
- subgroup-based validation checks
- local CV vs leaderboard gap checks

## Sampling / Weighting

- class weights, sample weights, subgroup weights
- under-sampling, over-sampling, balanced batches
- hard-example emphasis, outlier down-weighting
- pseudo-label confidence weighting

## Missingness Handling

- leave as native missing, median fill, mean fill, constant fill
- missing indicators, grouped imputations, rare-category fill
- missingness interaction features, missing-count features

## Categorical Preprocessing

- ordinal encoding
- one-hot encoding
- rare-bucket one-hot
- capped one-hot
- frequency encoding
- count encoding
- target encoding
- leave-one-out encoding
- hashing
- native categorical handling
- mixed categorical branches

## Numeric Preprocessing

- raw numeric features
- standard scaling
- robust scaling
- min-max scaling
- quantile transform
- rank-gauss style transforms
- log1p transforms
- clipping
- winsorizing
- binning
- polynomial features
- spline-like expansions

## Feature Generation

- row sums, row means, row std, row mins, row maxes
- row missing-count, row zero-count, row unique-count
- count features, frequency features, rarity features
- pairwise interactions, crosses, products, ratios, differences
- binned interactions, threshold flags, monotonic buckets
- groupby counts, groupby means, groupby target-free aggregates
- category-combination keys
- target-driven feature selection
- feature pruning, feature clustering, correlation pruning
- PCA, SVD, ICA, NMF, learned representations
- anomaly scores, isolation-style signals
- meta-features from secondary models

## Model Families

- logistic regression, ridge, lasso, elastic net
- linear SVM, kernel SVM
- kNN
- naive Bayes
- decision trees
- RandomForest
- ExtraTrees
- HistGradientBoosting
- LightGBM
- XGBoost
- CatBoost
- MLP
- wide-and-deep
- TabNet
- FT-Transformer
- mixture-style specialist models

## Tuning Directions

- depth, leaves, learning rate, iterations
- regularization, min child, min samples, gamma-style penalties
- row subsampling, column subsampling, feature bagging
- loss variants, objective variants, class weights
- early stopping, longer training, shorter training
- categorical-specific knobs
- calibration variants
- threshold-free ranking focus
- alternate seeds

## Stability / Repeatability

- seed sweeps
- repeat promising runs
- repeat weak runs that may be noise
- replicate with alternate fold seeds
- bagging across seeds
- bagging across folds

## Diversity Building

- alternate preprocessing branches
- alternate feature branches
- alternate model families
- alternate seeds
- alternate objectives
- alternate validation views
- weak-but-different components

## Ensembling

- simple average
- weighted average
- rank average
- geometric mean
- power mean
- constrained weight search
- hill climbing
- greedy selection
- stacking
- preprocessing-branch blends
- seed-bagged blends
- shortlist-only blends
- family-balanced blends

## Diagnostics / Sanity Checks

- OOF correlation
- error overlap
- disagreement analysis
- feature-drop tests
- ablations
- subgroup performance checks
- per-fold rank stability
- CV/LB mismatch checks
- leakage checks

## Moonshots

- pseudo-labeling
- self-training
- external data
- synthetic data
- transfer features
- pretraining
- teacher-student pipelines
- two-stage residual pipelines
- specialist submodels by subgroup
- mixture-of-experts style routing
- alternate objective shaping
- top-solution pattern import
- brute-force recipe sweeps
