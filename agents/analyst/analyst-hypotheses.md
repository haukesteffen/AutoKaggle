# Active Hypothesis

**Hypothesis:** MLP OOF predictions are meaningfully orthogonal to all three GBDT models (Pearson r < 0.990 with LGBM, CatBoost, and XGBoost).

**Context:** The scientist ran `mlp_baseline` (442ff2a, hidden=(256,256), relu, adam, early_stopping) and self-reported OOF r=0.9847 vs LGBM. This is below the 0.990 threshold used to reject XGBoost (r=0.9972) and CatBoost (r=0.9953/0.9972). If confirmed, MLP may add genuine diversity and improve an ensemble beyond the current CV ceiling of 0.916667.

**Allowed evidence:** Pearson and Spearman OOF correlation between MLP and each GBDT. Concise text only.

**Relevant experiments:**
- MLP: `442ff2aa236ea8a9d1552a406d77d16a3bb38f9f`
- LGBM: `cbef1de9024dbd5dc70988ba46baf1633f280340`
- CatBoost (default): `81151d814205733001448397276318fcfe9f5759`
- XGBoost: `16c521c99ec912a96ed068b0e38c70ad28bd4801`

**OOF pred paths:**
- MLP: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/442ff2aa236ea8a9d1552a406d77d16a3bb38f9f/oof-preds.npy`
- LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- CatBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/81151d814205733001448397276318fcfe9f5759/oof-preds.npy`
- XGBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/16c521c99ec912a96ed068b0e38c70ad28bd4801/oof-preds.npy`

**Decision criteria:** If MLP Pearson r < 0.990 with LGBM (confirmed), report the r values for all three pairs and recommend whether MLP is worth including in the ensemble weight grid search.
