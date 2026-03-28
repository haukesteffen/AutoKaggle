# Scientist Guidance

## Current Lane

Phase: Exploitation / Shortlist Building. Feature engineering and model diversity are closed — all paths exhausted on day 1. The remaining work is ensemble composition and one MLP probe.

**Shortlist components:**
- LGBM: `cbef1de9024dbd5dc70988ba46baf1633f280340` (CV 0.915855)
- CatBoost: `81151d814205733001448397276318fcfe9f5759` (CV 0.916405)
- XGBoost: `16c521c99ec912a96ed068b0e38c70ad28bd4801` (CV 0.916421)

OOF preds at: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>/oof-preds.npy`

## Harness Path Fix — Always Required

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## Priority Ideas

1. **3-way ensemble: LGBM + CatBoost + XGBoost simple average** — Load OOF preds from all three shortlist components, average them, and run through the harness. `EXPERIMENT_NAME = "ensemble_lgbm_catboost_xgb_avg"`. Strategist computed this as CV ~0.916592 from OOF preds — run it to confirm and generate test predictions for submission.

2. **OOF weight grid search (3-way)** — Using the same three OOF preds, grid-search weights in steps of 0.1 (w_lgbm + w_cb + w_xgb = 1.0, all ≥ 0.0). Find the weight combination with highest OOF CV, then run through harness with that weighting. `EXPERIMENT_NAME = "ensemble_3way_weighted_opt"`. If CV improves above 0.916592, keep it.

3. **Fast MLP probe** — A single `MLPClassifier(hidden_layer_sizes=(256, 256), activation='relu', solver='adam', early_stopping=True, max_iter=200, random_state=42)` in a Pipeline with the same preprocessor as LGBM. `EXPERIMENT_NAME = "mlp_baseline"`. Goal is not to beat GBDT solo — it's to check if OOF is genuinely more orthogonal (r < 0.990 with LGBM). If the supervisor confirms orthogonality, they'll try adding it to the ensemble.

4. **LR as small-weight ensemble component** — The LR OOF preds already exist from experiment `4bc520f`. Try averaging LGBM + CatBoost + XGBoost + LR with LR weight 0.05–0.10. Compute OOF CV offline first; only run through harness if it improves above 0.916592.

## Avoid Entirely

- Feature engineering (target encoding, interaction features, count features — all tried, no gain)
- ExtraTrees or RandomForest in ensembles (too weak, dragged all blends below baseline)
- CatBoost tuning (OOM at depth 8+, tuned d7 more correlated with LGBM than default)
- XGBoost tuning (already in shortlist; more tuning increases LGBM correlation)
- Stacking or meta-learners

## Why

Strategist confirmed: all GBDT models are r>0.990 OOF correlation with LGBM. Feature engineering doesn't help because tree models already find those splits. The ceiling is ~CV 0.9166. Remaining upside: ensemble weight optimisation (+0.0001–0.0003), MLP probe (if orthogonal). Run these in order.
