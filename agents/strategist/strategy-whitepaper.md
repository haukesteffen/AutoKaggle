# Strategy Whitepaper

## Current Date
March 29, 2026

## Deadline
March 31, 2026

## Days Remaining
3 (March 29, March 30, March 31) — 15 slots total (5+5+5)

## Current Phase
**Final consolidation — exploration complete, all lanes exhausted**

## Status Summary

Every major strategy lane has been fully explored and closed:

- **Feature engineering** — three families tried; none improved CV; closed.
- **GBDT solo tuning** — all variants within ±0.0001 CV of baseline; closed.
- **Bagging models (ExtraTrees, RandomForest)** — solo CV 0.910–0.911; too weak; closed.
- **MLP ensemble** — r=0.985 OOF correlation vs LGBM confirmed orthogonality, but solo CV of 0.911 is 0.005 below the GBDT ceiling. Full harness test showed adding MLP at 10% weight reduced CV by 0.0003 vs equal 3-way GBDT. Closed.
- **OOF-tuned CB+XGB (no LGBM)** — CB=0.5/XGB=0.5 gave CV=0.916381, worse than equal 3-way. Closed.
- **OOF weight grid (LGBM+CB+XGB, step=0.05)** — best combo LGBM=0.05/CB=0.50/XGB=0.45 gives OOF 0.916657 vs equal-weight OOF 0.916580 (+0.000077). Delta is smaller than OOF estimation noise; OOF-to-harness transfer has failed twice. Not worth implementing.
- **LR as ensemble component** — weaker solo than MLP; no orthogonality advantage; closed.

**The ceiling is definitively CV=0.916540, LB=0.91396 (commit 7b386f5, equal-weight LGBM+CB+XGB).**

## Consolidation Posture

7b386f5 is the final candidate. No further exploration is planned.

**Planned use of remaining slots:**

| Date | Slots | Action |
|------|-------|--------|
| March 29 | 5 available | Hold; no experiment warrants a submission today |
| March 30 | 5 available | 1 insurance re-submission of 7b386f5 (confirms the score holds) |
| March 31 | 5 available | 1 final submission of 7b386f5 as the official entry |
| Reserve | — | 1–2 slots held across March 29–31 in case a genuinely new lane appears |

Realistically expect to use 2–3 of the 15 remaining slots.

## Guidance For The Supervisor

1. **7b386f5 is the anchor and the final answer.** Equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396.

2. **No new experiments unless a genuinely novel model family appears.** The known families (GBDT, bagging, MLP, LR) are all exhausted. If the scientist brings a credible new idea (e.g. a model family not yet tried) the team can still act on it — but the bar is high: offline harness CV must clearly exceed 0.9168 before spending an LB slot.

3. **OOF estimates are not sufficient to trigger a submission.** OOF-to-harness transfer has failed twice. Any candidate must be validated with the full harness CV first.

4. **Do not invent experiments to fill slots.** The remaining budget exists as insurance, not as an invitation to explore.

5. **CV/LB gap is stable at ~0.0026** across all scored submissions. CV remains a reliable proxy for LB.

## Closed Lanes (Do Not Revisit)

- MLP in any ensemble weight
- LR in any ensemble weight
- OOF-tuned weight optimisation (LGBM+CB+XGB or any subset)
- OOF-tuned CB+XGB without LGBM
- ExtraTrees / RandomForest
- CatBoost depth tuning (OOM above depth 7; closed)
- LGBM hyperparameter tuning
- Feature engineering (any family)
- XGBoost solo tuning
- Stacked meta-learners

## Pivot Conditions

- **No hard gates.** If the scientist surfaces a genuinely new model family or a structural insight not yet tested, the team may act — but offline harness CV must clearly beat 0.9168 before any LB slot is used.
- If any LB submission returns below 0.9135: flag CV/LB gap widening to analyst before spending further slots.
- If 7b386f5 re-submission on March 30 scores materially different from 0.91396: investigate before submitting on March 31.

## Why This Is The Final State

30+ experiments and 5+ LB submissions have been run. The GBDT diversity wall is confirmed (all three boosting families r > 0.990 OOF correlation). The equal-weight LGBM+CB+XGB ensemble has beaten every alternative attempted, including OOF-optimised variants. The OOF weight grid confirmed that no weight vector within the GBDT shortlist meaningfully improves over equal weighting once harness noise is accounted for. There is no remaining lever with a credible expected gain above the noise floor. LB=0.91396 is the team's best achievable result on this feature set.

---
*Refreshed: March 29, 2026. Final consolidation. 30+ experiments, 5+ LB submissions. All lanes exhausted. Current best: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396.*
