# Memory

## Competition Facts

- S6E4 `Predicting Irrigation Need` is a multiclass task (`High`, `Low`, `Medium`) scored by balanced accuracy.
- Train/test are large and clean: 630,000 train rows, 270,000 test rows, no missingness, no meaningful train/test shift, and no obvious leakage.
- Class balance is severe: `High` is about 3.3%, so reweighting or other balancing remains necessary.
- Kaggle submission limit is 5 per day.
- Deadline assumption is 2026-04-30.

## Current Policy

- Phase: feature engineering. Priority is expanding the feature space and model diversity, not refining the stacking layer.
- The S-089 to S-106 stacking micro-optimization lane is retired (18 experiments, +0.0004 total, plateau detected). The next stacking rebuild happens after the model zoo has 8+ diverse base models on an expanded feature set.
- Feature engineering ideas are tracked in `state/backlog.md`. Base model inventory is tracked in `state/portfolio.md`.
- Promotion threshold for submission: CV improvement > 0.001 over best submitted (S-094 at 0.972299 CV / 0.97144 LB).
- Analyst capacity: use for diversity checks, feature importance, error analysis, and data exploration — not just promotion gates.

## Active Model Read

- S-094 is the best submitted stack (0.97144 LB, rank 157). S-105 is the best offline score (0.972308) but failed the behavior gate.
- The stacking layer has plateaued. Further gains require expanding the base: new features and more diverse base models.
- The portfolio has only 4 base models (S-014 XGB, S-082 LGBM, S-073 MLP, S-052 LR). Grandmaster standard is 10+.
- All base models use similar basic features. No GroupBy stats, no target encoding, no frequency encoding, no categorical interactions have been tried.

## Durable Signals

- `Soil_Moisture` is the strongest single numeric signal and behaves nonlinearly around a threshold near 20.
- Low `Soil_Moisture` plus low `Rainfall` is the strongest High-class region; low `Soil_Moisture` plus high `Temperature` is the next strongest.
- Crop-specific effects exist under low `Soil_Moisture`; `Maize` and `Sugarcane` are stronger than `Rice`.
- `S-014` showed excellent fold stability and strong High recall, so the engineered signal stack is real, not noise.

## Submission Lessons

- Early submissions stayed within a tight CV/LB alignment band of roughly 0.003, so local gains have generally transferred.
- Public rank movement can reflect board movement as much as model change, so rank alone is not a reliable regression signal.

## Caution Flags

- `S-102` is not a safe simplification target; its harmful true-`Medium` regressions are spread across folds.
- `S-104` shrinkage did not meaningfully improve the Medium-behavior gate.
- Higher CV alone is insufficient; true-`Medium` reallocation and fold safety must improve together.
- Repeated `S-052` Medium-residual repair attempts now collapse to zero shrinkage on both the `S-094` and `S-105` bases.
- Avoid spending analyst time on low-value attribution cleanup or leaderboard probing when no new candidate is ready.

## Retired Work

- Pure simplification of `S-094` through `S-102` is retired.
- The `S-104` shrinkage lane is retired.
- The `S-106` Medium-only residual replacement lane on top of `S-094` is retired.
- The `S-107` joint stabilization lane (`S-105` High/Low shrinkage plus added Medium residual repair) is retired.
- `S-105` is the best offline score, but not a promoted replacement.
- The S-089 to S-107 stacking micro-optimization lane is retired (18+ experiments, +0.0004 total, plateau detected).
