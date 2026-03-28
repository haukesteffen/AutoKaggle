# Strategy Idea Cookbook

This file is owned by the strategist role.

It is a reusable menu of strategic plays. It should remain broadly useful across runs and should not turn into a run-specific journal.

For each play, state:

- when to use it
- why it might help
- what evidence should justify trying it
- what evidence should cause it to be deprioritized

## Baseline Anchors

### Simple linear baseline

- When to use it: at the very start of a run or when the team needs a reproducible sanity anchor
- Why it might help: establishes a trustworthy floor and exposes whether the feature space is already strong
- Try it if: there is no anchor yet or the scientist has drifted too quickly into complexity
- Deprioritize if: a solid anchor already exists and later work is clearly above it

### Regularized linear variants

- When to use it: after the basic linear anchor is in place
- Why it might help: can improve calibration, robustness, or future ensemble value with low complexity
- Try it if: the strategy calls for a stronger linear component or a simple ensemble ingredient
- Deprioritize if: repeated linear variants produce no meaningful movement

### First strong tree baseline

- When to use it: early, once the simplest anchor exists
- Why it might help: quickly establishes the likely single-model strength of the tabular problem
- Try it if: the team needs to know whether tree models are the primary frontier
- Deprioritize if: the frontier has already moved to refinement or late-phase discipline

## Stronger Single-Model Families

### LightGBM / XGBoost refinement

- When to use it: once a tree anchor exists and there is evidence that a single model can still move materially
- Why it might help: these models often provide the strongest single-model performance on tabular Playground tasks
- Try it if: the team still lacks a strong leaderboard anchor or the current best single model is not yet convincing
- Deprioritize if: late-stage work favors shortlist stability over more tree tuning

### CatBoost / native categoricals

- When to use it: when the feature mix suggests categorical handling may be decisive
- Why it might help: can unlock signal where one-hot approaches are brittle or lossy
- Try it if: analysis shows categorical structure is central or native-cat trials have promise
- Deprioritize if: repeated evidence shows native categorical handling is worse on this competition

### CatBoost tuned for divergence (not just strength)

- When to use it: when CatBoost default is already in the shortlist but ensemble gain is small because it is too correlated with LGBM
- Why it might help: CatBoost at default settings often follows similar gradient contours to LGBM. Lower learning rate (0.03), more iterations (1500–2000), higher depth (8–10), and feature subsampling (rsm=0.7) can push CatBoost into different feature interactions, making it a more useful ensemble partner
- Try it if: LGBM+CatBoost ensemble adds less than +0.001 LB over LGBM alone — this is a sign of correlation, not complementarity
- Deprioritize if: tuned CatBoost still tracks LGBM closely in CV (difference < 0.0003 in ensemble gain)

### Reweighted or calibrated variants

- When to use it: when imbalance, calibration drift, or threshold behavior may matter
- Why it might help: can improve ranking quality or make a model more ensemble-friendly
- Try it if: analysis highlights class imbalance or unreliable probability shape
- Deprioritize if: the metric is insensitive and the modifications consistently fail

## Diversity-Building Plays

### Model-family diversification

- When to use it: after at least one strong anchor exists
- Why it might help: different model families can add ensemble value even when their standalone CV is slightly worse
- Try it if: the strategy objective includes future ensembling or the current best family appears exhausted
- Deprioritize if: time is short and there is no realistic path to using the diversity

### ExtraTrees / Random Forest as bagging-family diversity component

- When to use it: when LGBM and CatBoost are both in the shortlist but ensemble gain is small due to high correlation between two boosting-family models
- Why it might help: bagging models (ExtraTrees, RandomForest) have structurally different error patterns from boosting models. They reduce variance through averaging independently-grown trees rather than through sequential correction of residuals. This makes them naturally more orthogonal to LGBM/CatBoost even when their standalone CV is somewhat lower
- Try it if: LGBM+CatBoost correlation is high (ensemble gain < +0.001 LB) and there is still time for a diversity experiment
- Deprioritize if: ensemble gain from adding the bagging component is still negligible after tuning, or if the standalone CV is more than 0.003 below the best boosting model (the diversity gain rarely overcomes that gap)
- Suggested starting point: ExtraTreesClassifier n_estimators=500, max_features="sqrt", min_samples_leaf=5; or RandomForestClassifier with similar settings

### Feature-space diversification

- When to use it: when multiple credible preprocessing routes exist
- Why it might help: different feature constructions can create complementary errors
- Try it if: analysis suggests alternative representations may capture different structure
- Deprioritize if: the team is still missing a strong baseline anchor

### Preprocessing diversity

- When to use it: once the scientist has a stable implementation baseline
- Why it might help: simpler preprocessing changes can sometimes yield diversity without a full model-family switch
- Try it if: time budget is moderate and the likely payoff is better ensemble complementarity
- Deprioritize if: the same family and preprocessing stack already dominate all evidence

## Ensemble Construction Ideas

### Simple averaging

- When to use it: once at least two credible components exist
- Why it might help: low-risk first ensemble test with minimal complexity
- Try it if: components are meaningfully different and individually competent
- Deprioritize if: there are not yet two believable components

### Weighted averaging

- When to use it: after simple averaging establishes that combination is worthwhile
- Why it might help: can extract more value from uneven component quality
- Try it if: one component is clearly stronger but diversity still matters
- Deprioritize if: component instability makes weight tuning noisy

### Stacked linear meta-models

- When to use it: once the shortlist is stable enough to justify coordination cost
- Why it might help: can combine strong and weakly complementary models more intelligently than a raw average
- Try it if: OOF predictions are available and the strategy calls for serious ensemble work
- Deprioritize if: the deadline is too near for careful validation

### Shortlist-only ensembles late in the competition

- When to use it: in the late phase, when exploration budget is shrinking
- Why it might help: narrows work to high-confidence ingredients instead of endlessly growing the candidate pool
- Try it if: the team already has a shortlist and wants disciplined final optimization
- Deprioritize if: the run is still in broad exploration and the shortlist is premature

## Simplification / Pruning Plays

### Remove weak features

- When to use it: when analysis identifies persistently low-value or noisy inputs
- Why it might help: can reduce complexity while preserving or improving score
- Try it if: importance or ablation evidence is strong
- Deprioritize if: the evidence is ambiguous and the change would create brittle special cases

### Remove brittle preprocessing

- When to use it: when the current stack contains hacks that are not paying for themselves
- Why it might help: simpler systems are easier to iterate on and often generalize better
- Try it if: the complexity cost is high relative to the observed score gain
- Deprioritize if: the preprocessing is central to the current best model

### Simplify without material score loss

- When to use it: whenever two approaches are close in score but far apart in complexity
- Why it might help: creates more reliable components and easier future ensembling
- Try it if: the simpler variant is near-parity
- Deprioritize if: the simpler variant clearly loses too much

## Validation / Robustness Diagnostics

### Fold instability investigation

- When to use it: when fold variance is high or one fold repeatedly behaves differently
- Why it might help: can reveal overfitting, leakage, or brittle preprocessing
- Try it if: results are noisy enough that rank-ordering experiments is difficult
- Deprioritize if: fold behavior is already stable

### CV/LB mismatch investigation

- When to use it: after leaderboard submissions start disagreeing with CV
- Why it might help: this is one of the strongest signals that the current validation strategy is misleading
- Try it if: LB gains stop tracking CV gains
- Deprioritize if: there is still no LB evidence at all

### Leakage checks

- When to use it: whenever scores move suspiciously fast or diagnostics look too good
- Why it might help: catching leakage early prevents the team from optimizing the wrong thing
- Try it if: feature behavior or leaderboard behavior looks implausible
- Deprioritize if: there is no concrete reason to suspect leakage and time is extremely short

## Late-Phase Conservative Plays

### Prioritize reproducible high-confidence models

- When to use it: in the final days of the competition month
- Why it might help: stable high-confidence components are more valuable than speculative novelty near the deadline
- Try it if: time remaining is short and the shortlist is already credible
- Deprioritize if: the run is still missing a single strong anchor

### Reduce novelty near deadline

- When to use it: when the remaining submission budget is scarce
- Why it might help: prevents spending final bandwidth on low-confidence experiments
- Try it if: the strategy whitepaper classifies the run as exploitation or final submission discipline
- Deprioritize if: the current path is clearly exhausted and no credible shortlist exists

### Spend submissions on signal extraction, not speculative breadth

- When to use it: once there are only a few submissions left
- Why it might help: leaderboard slots become information resources that must be spent deliberately
- Try it if: the team needs to distinguish between a small set of serious candidates
- Deprioritize if: the run is still so early that broad anchoring is more valuable

## Cold-Start / Late-Entry Plays

### Front-load model-family comparison when time is short

- When to use it: when the run starts with 3 or fewer days remaining and no experiments have been run
- Why it might help: the most information-dense question in tabular Playground competitions is whether tree models are dominant over linear ones; answering it on day one determines the allocation for all remaining work
- Try it if: the run is in bootstrap phase with no LB history
- Deprioritize if: model-family comparison is already settled from prior experiment history

### Linear anchor before tree exploration

- When to use it: always, at the very start of a cold run
- Why it might help: provides a reproducible reference point; reveals if the feature space is already well-conditioned; identifies whether leakage or fold issues exist before committing tree-model iterations
- Try it if: `experiment.py` contains a usable baseline that has not yet been evaluated
- Deprioritize if: a strong, validated anchor already exists from a prior run or prior day

### Compress to two-model ensemble when deadline is within 3 days

- When to use it: when fewer than 4 days remain and no shortlist exists
- Why it might help: in constrained time, a simple average of the best linear model and the best tree model is often more reliable than chasing a third family or complex stacking; it avoids late-phase validation debt
- Try it if: two distinct model families have been evaluated and both have validated CV scores
- Deprioritize if: one model family is clearly dominant and there is no complementary diversity to gain

## Tuning Failure Patterns

### Hyperparameter tuning often stalls near the tree model ceiling

- When to recognize it: when num_leaves, n_estimators, learning_rate, and min_child_samples all return to approximately the same CV score
- Why it happens: on Playground Series datasets, the tree model ceiling on the given feature set is often hit quickly with conservative defaults. The signal that tuning has stalled is when 3+ tuning variants all land within ±0.0001 CV of the baseline
- What to do instead: pivot to feature engineering or model-family diversity rather than continuing to tune the same model family
- Evidence from mar28: LGBM num_leaves=63, deeper LGBM (1000 iterations lr=0.03), target encoding, and count features all failed to beat LGBM baseline CV 0.915855; all variants were within 0.0001 of baseline

### Target encoding rarely helps tree models as a solo feature

- When to recognize it: when TargetEncoder applied to high-variation categorical columns produces no CV gain on LGBM or CatBoost
- Why it happens: gradient boosted trees already learn effective splits on categorical features (especially CatBoost with native categories). Target encoding pre-computes an average that the tree can already discover internally
- What might still be useful: target-encoded features may add diversity when used in a different model family (e.g. as extra inputs to a logistic regression stack member), but this is speculative
- Evidence from mar28: TargetEncoder on 13 high-variation columns: CV 0.915805 vs baseline 0.915855, discarded

## ROC-AUC / Binary Classification Notes

### Calibration may matter less than ranking

- When to use it: as a reminder when tuning probability outputs
- Why it might help: ROC-AUC is rank-based; well-calibrated probabilities are not required for the metric, so calibration fixes are low-priority unless ensemble weighting relies on them
- Try it if: an analyst finding suggests calibration drift is affecting ensemble blending
- Deprioritize if: the team is still in the anchoring phase

### Class imbalance treatment requires analyst confirmation

- When to use it: before applying class weights, oversampling, or threshold adjustments
- Why it might help: treating a balanced dataset as imbalanced can hurt ROC-AUC; analyst should confirm the actual class distribution before the scientist applies imbalance corrections
- Try it if: the churn rate appears low or the scientist proposes imbalance-specific changes
- Deprioritize if: the analyst has already confirmed balanced class distribution
