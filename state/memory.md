# Memory

## Competition Facts

- S6E4 `Predicting Irrigation Need` is a multiclass task (`High`, `Low`, `Medium`) scored by balanced accuracy.
- Train/test are large and clean: 630,000 train rows, 270,000 test rows, no missingness, no meaningful train/test shift, and no obvious leakage.
- Class balance is severe: `High` is about 3.3%, so reweighting or other balancing remains necessary.
- Kaggle submission limit is 5 per day.
- Deadline assumption is 2026-04-30.

## Current Policy

- Current run is in a late promotion gate, not an exploration phase.
- Promote only when offline balanced accuracy beats `0.972299` by a real margin, or matches it with clearly better true-`Medium` behavior and a safer fold pattern than `S-102`.
- Analyst capacity is for a narrow promotion question after a new candidate exists.
- Keep conservative variants close to `S-094`.

## Active Model Read

- The highest-value lane is controlled replacement or stabilization of the noisy `S-052` contribution inside the `S-094` stack.
- `S-105` is the best offline challenger so far, but it still failed the behavior gate.
- `S-094` is the best submitted stack so far at `0.97144` LB, rank `157`, submitted on 2026-04-04.
- More attribution cleanup on `S-102` and leaderboard probing are low value unless a new candidate changes the decision.

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
- Avoid spending analyst time on low-value attribution cleanup or leaderboard probing when no new candidate is ready.

## Retired Work

- Pure simplification of `S-094` through `S-102` is retired.
- The `S-104` shrinkage lane is retired.
- `S-105` is the best offline score, but not a promoted replacement.
