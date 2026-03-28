# Active Hypothesis

**Hypothesis:** Are the OOF predictions from LGBM baseline (cbef1de) and CatBoost baseline (81151d8) highly correlated — specifically, is the Pearson correlation of their OOF probability scores above 0.95?

**Decision if supported (correlation ≥ 0.95):** The two models are near-redundant as ensemble components. Prioritize finding a more orthogonal third model (e.g. ExtraTrees). A simple average ensemble of these two is unlikely to add meaningful diversity.

**Decision if rejected (correlation < 0.95):** The models have meaningful disagreement. The small ensemble LB gain (+0.00064) may reflect ensemble construction or weighting issues rather than model redundancy. Consider weighted averaging or investigating where the two models disagree most.

**Allowed evidence:** Pearson correlation of OOF scores, rank correlation (Spearman), fold-level agreement metrics, and concise text only. No plots.

**Relevant experiments:** cbef1de (lgbm_baseline, CV 0.915855), 81151d8 (catboost_baseline, CV 0.916405)

OOF pred paths:
- `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/81151d814205733001448397276318fcfe9f5759/oof-preds.npy`
