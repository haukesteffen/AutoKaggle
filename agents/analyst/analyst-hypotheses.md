# Active Hypothesis

**Hypothesis:** Is the tuned CatBoost (`b822216`, depth=7, iter=1000, rsm=0.8) less correlated with LGBM baseline (`cbef1de`) than the default CatBoost (`81151d8`) was — specifically, is the Pearson OOF correlation between tuned CatBoost and LGBM below 0.990 (vs 0.9953 for default CatBoost)?

**Decision if supported (correlation < 0.990):** The tuned CatBoost adds meaningful diversity despite its weaker solo CV. Direct the scientist to build an ensemble of LGBM + tuned CatBoost and check if it beats the current best (CV 0.916530).

**Decision if rejected (correlation ≥ 0.990):** Tuned CatBoost is not meaningfully more orthogonal than default CatBoost. Skip the ensemble with tuned CatBoost and direct the scientist to the mtm_fiber interaction feature experiment instead.

**Allowed evidence:** Pearson and Spearman OOF correlation between tuned CatBoost and LGBM. Concise text only. No plots.

**Relevant experiments:** cbef1de (lgbm_baseline), b822216 (catboost_tuned_d7)

OOF pred paths:
- LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- Tuned CatBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/b822216261dbc9aa0df689fe2e5fd5ab779c6261/oof-preds.npy`
