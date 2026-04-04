# Supervisor Run State
generated_at: 2026-04-04T17:41Z
generated_by: harness.supervisor_snapshot

Compact restart context for Codex supervisor sessions. Read this before any full histories.

## Default Read Set
- `AGENTS.md`
- `agents/program.md`
- `agents/supervisor/role.md`
- this file

## Current Strategy
- current_date: April 4, 2026
- deadline_assumption: April 30, 2026 — last calendar day of the competition month (S6E4 default assumption).
- days_remaining: 26
- primary: Exploit the validated XGB+LGBM ensemble lane (55%)
- secondary: Controlled diversity expansion around the ensemble anchor (25%)
- background: Leaderboard calibration and submission discipline (15%)
- hold: Further manual feature engineering and weak third-leg blends from current components (5%)
- guidance:
  1. Treat `S-083` as the new anchor. The baseline to beat is no longer `S-014`; it is the `0.70 x S-014 + 0.30 x S-082` blend. Near-term scientist work should focus on bounded refinements around that pair: fine-grained weight search near 0.70/0.30, seed diversity, or a simple stacker using existing OOF artifacts.
  2. Do not spend more runs on the current `HistGBM` third-leg path unless a new HistGBM variant closes most of the standalone gap first. `S-087` already answered the immediate question: the present 3-way blend does not improve the best 2-way blend.
  3. Keep one diversity lane alive, but raise the bar. New standalone candidates should either reach roughly 0.9700 CV or show materially different OOF behavior relative to `S-083`. Weak-but-different models are no longer enough by themselves; they now need a clearer path to ensemble gain.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 86
- scored_results: 82
- terminal_non_scored_results: 4
- best_cv: 0.971177 (S-083) | Weighted blend XGB+LGBM: alpha=0.7×XGB(S-014) + 0.3×LGBM(S-082) OOF; sweep over [0.9,0.8,0.7,0.6,0.5,0.4,0.3] — best at alpha=0.7, positive lift over S-014 XGB-only baseline (0.970856)
- recent_results:
  - S-084 | 0.954218 | LGBM n=2000 lr=0.02 num_leaves=7 min_child_samples=100 subsample=0.9 colsample_bytree=0.8 balanced, SM²+OrdinalEncoder — too aggressively regularized (num_leaves=7 underfits vs 15 in S-082: 0.970657, large regression -0.016638 vs S-014)
  - S-085 | 0.970782 | XGB n=1000 lr=0.025 depth=5 subsample=0.8 colsample_bytree=0.8 balanced, SM²+StandardScaler+OHE — slower learning with 2× trees does not improve over S-014 (0.970856); slightly below standalone XGB best
  - S-086 | 0.969934 | HistGBM max_iter=1500 lr=0.02 max_leaf_nodes=15 min_samples_leaf=50 l2_reg=0.1 class_weight=balanced, SM²+OrdinalEncoder — tuned toward LGBM params; 0.969934 close to S-018 (0.969459) but below XGB/LGBM best; note subsample not available in sklearn HistGBM, removed; marginal improvement over S-018 (+0.000475) insufficient for 3-way blend at current best 0.971177
  - S-087 | 0.971124 | Weighted blend XGB+LGBM+HistGBM: sweep [(0.6,0.3,0.1),(0.6,0.25,0.15),(0.5,0.35,0.15),(0.55,0.3,0.15),(0.65,0.25,0.10)] on S-014/S-082/S-086 OOF; best at (0.55,0.30,0.15), slightly below S-083 (0.971177)
  - S-088 | 0.971161 | Fine XGB+LGBM blend sweep on S-014/S-082 OOF over alpha=[0.64,0.66,0.68,0.69,0.70,0.71,0.72,0.74,0.76]; near-anchor search stayed just below S-083

## Analysis Summary
- knowledge_entries: 29
- findings_entries: 11
- recent_knowledge:
  - AK-025 | Candidate Threshold Indicators from A-006 Are DEPLETED Zones (Not Enriched) | The three A-006 candidate indicators are in heavily depleted High-class zones, not enriched ones:
  - AK-027 | MLP(64,32) is Strongly Diverse from LR on S-040 Feature Set | MLPClassifier(hidden=(64,32), relu, max_iter=500, early_stopping=True) on the S-040 feature set:
  - AK-028 | S-045 MLP is Too Correlated with S-014 XGBoost to Ensemble Beneficially | S-045 MLP (CV=0.9618) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
  - AK-029 | S-052 LR is More Diverse from S-014 XGBoost Than S-045 MLP Was | S-052 LR (CV=0.9286) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
- recent_findings:
  - A-009 | verdict=supported | conf=high | q=Does the MLPClassifier (2-layer shallow neural net, hidden layers 64 and 32) have a structural advantage over Logistic Regression on the S-040 feature set — specifically, does it produce meaningfully different OOF predictions from LR (correlation < 0.97), suggesting it would add diversity value for ensembling even if CV score is similar?
  - A-010 | verdict=rejected | conf=high | q=Do the S-045 MLP OOF predictions (0.9618 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: do the two models disagree on a material fraction of High-class samples in a way that suggests ensemble gains are possible?
  - A-011 | verdict=supported | conf=high | q=Do the S-052 LR OOF predictions (0.9286 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: does S-052 recover a meaningful fraction of High-class TPs that S-014 misses, suggesting ensemble value?

## Leaderboard
- submissions_total: 3
- best_lb: 0.96867 (S-083) | rank 233
- latest_submission: S-083 | 2026-04-04T16:54Z | 0.96867 | First positive ensemble signal; validate 0.70×S-014 XGB + 0.30×S-082 LGBM against the S-014 anchor

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
