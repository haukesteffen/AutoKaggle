# Active Hypothesis

**Hypothesis:** Is the XGBoost baseline (`16c521c`, n=500, lr=0.05, depth=6) OOF correlation with LGBM baseline (`cbef1de`) below 0.990 — i.e., meaningfully more orthogonal than default CatBoost (r=0.9953)?

**Decision if supported (Pearson r < 0.990):** XGBoost adds genuine ensemble diversity. Direct the scientist to try LGBM + XGBoost simple average ensemble.

**Decision if rejected (Pearson r ≥ 0.990):** XGBoost is also near-redundant with LGBM. Skip the LGBM + XGBoost ensemble and focus entirely on the mtm_fiber interaction feature experiment to shift LGBM's prediction space.

**Allowed evidence:** Pearson and Spearman OOF correlation between XGBoost and LGBM. Concise text only. No plots.

**Relevant experiments:** cbef1de (lgbm_baseline), 16c521c (xgb_baseline)

OOF pred paths:
- LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- XGBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/16c521c99ec912a96ed068b0e38c70ad28bd4801/oof-preds.npy`
