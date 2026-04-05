# Analysis Ledger

Append one compact row per completed analyst answer.
Keep raw evidence, long stdout, and detailed comparison output in `artifacts/<task_id>/`; this ledger records only the decision summary.

| analysis_id | at | q | verdict | confidence | artifact_dir | summary |
|-------------|----|---|---------|------------|--------------|---------|
| A-001 | 2026-04-01T20:02Z | data_quality_issues | supported | high | - | No missingness, leakage, or train/test shift; only severe 17.6:1 class imbalance is material. |
| A-002 | 2026-04-01T22:24Z | soil_moisture_nonlinearities | supported | high | - | Supported SM^2 plus low-SM/low-rain and low-SM/high-temp indicators; humidity and season were weak. |
| A-003 | 2026-04-02T00:08Z | s014_fold_and_subgroup_stability | supported | high | - | S-014 is stable; weakest pockets are fold 0 and High recall in East, Rabi, and Sugarcane. |
| A-004 | 2026-04-02T19:42Z | linear_model_signal | supported | high | - | Linear signal favors StandardScaler plus SM^2, SM<20 binning, log-rainfall, and SM x rain/temp terms. |
| A-005 | 2026-04-02T19:53Z | s032_low_sm_low_rain_indicator | rejected | high | - | Rejected: S-032 already recalls High well inside SM<20 & Rain<1000, so that indicator is unlikely to help. |
| A-006 | 2026-04-02T19:57Z | s032_out_of_subgroup_fn_regions | supported | high | - | Supported: most S-032 High false negatives sit outside the core subgroup, especially SM>=35 and cooler regions. |
| A-007 | 2026-04-02T20:06Z | a006_indicator_selectivity | rejected | high | - | Rejected: the A-006 zones have poor High enrichment, so their selectivity is too weak for LR features. |
| A-008 | 2026-04-02T20:21Z | target_encoding_vs_ohe_for_lr | rejected | high | - | Rejected: fold-safe target encoding trailed OHE on the same LR feature set by about 0.0004 BA. |
| A-009 | 2026-04-03T06:45Z | mlp_vs_lr_diversity | supported | high | - | Supported: the 64x32 MLP has materially different OOF probabilities from LR and can add ensemble diversity. |
| A-010 | 2026-04-03T07:02Z | s045_vs_s014_ensemble_value | rejected | high | - | Rejected: S-045 is diverse vs S-014, but simple ensembling still regresses against XGB alone. |
| A-011 | 2026-04-03T12:18Z | s052_vs_s014_ensemble_value | supported | high | - | Supported: S-052 recovers useful unique High cases with low correlation to S-014, but needs weighted blending. |
| A-012 | 2026-04-04T18:05Z | s073_three_way_checkpoint | rejected | high | - | Rejected: S-073 is less correlated, but the simple 3-way average regresses sharply versus S-083. |
| A-013 | 2026-04-04T18:19Z | s052_diversity_after_s093 | rejected | high | - | Rejected: S-052 remains less correlated with S-093 than the tree pair, but the simple average is too harmful. |
| A-014 | 2026-04-04T19:11Z | s094_recovery_pattern | rejected | high | - | Rejected: S-094's tiny lift is mostly Medium cleanup, not durable High recovery from S-052. |
| A-015 | 2026-04-04T20:06Z | s052_medium_signal_attribution | supported | high | - | Supported: S-052's contribution in S-094 is mainly Medium-class probability signal, not direct High recoveries. |
| A-016 | 2026-04-04T20:13Z | s102_simplified_incumbent_gate | rejected | high | - | Rejected: S-102 keeps BA close to S-094 but adds new High regressions and fails the behavior gate. |
| A-017 | 2026-04-04T20:15Z | s102_medium_regressions_by_fold | rejected | high | - | Rejected: harmful S-102 Medium regressions are spread across folds, not concentrated in one fold. |
| A-018 | 2026-04-05T07:51Z | s104_shrinkage_behavior_gate | rejected | high | - | Rejected: S-104 improves Medium behavior vs S-102 and stays near S-094 BA, but not enough to continue. |
| A-019 | 2026-04-05T08:07Z | s105_behavior_gate | rejected | high | - | Rejected: S-105 beats S-094 on BA and stays under the High-regression cap, but Medium reallocations stay net negative. |
