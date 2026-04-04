# Strategy Whitepaper

## Current Date
April 4, 2026

## Deadline Assumption
April 30, 2026 - last calendar day of the competition month (S6E4 default assumption).

## Days Remaining
26

## Read

- 87 scientist runs are logged, with 83 scored and enough coverage to treat the current decision as an ensemble-selection problem, not a model-family discovery problem.
- `S-089` is the new local best at 0.971927 CV, beating the `S-083` anchor by +0.000750 CV through multinomial logistic regression stacking over `S-014` and `S-082` probabilities.
- `S-083` remains the best submitted run at 0.971177 CV / 0.96867 LB, so the current gap between local optimum and submitted optimum is now actionable.
- Recent refinement around the `S-083` blend has stalled: `S-087` scored 0.971124 and `S-088` scored 0.971161, which argues against more time on the current HistGBM third-leg path.
- CV/LB calibration is still acceptable; `S-005`, `S-014`, and `S-083` all stayed within a sub-0.003 CV/LB gap band, so the main risk is not calibration drift but failing to convert the new stacker gain into a stable submission.

## Emphasis

Primary: Exploit the stacking lane around `S-089` and verify whether the gain survives on the leaderboard
Secondary: Search for one more complementary base prediction source or stacker variant that can improve over the current two-model stack
Background: Maintain calibration checks and submission discipline so the next probe is informative
Hold: More work on the current HistGBM third-leg branch and manual feature engineering without a clear path to ensemble gain

## Guidance For The Supervisor

1. Treat `S-089` as the current research anchor and `S-083` as the submission baseline. The near-term question is whether the multinomial stacker can be reproduced cleanly enough to justify a leaderboard probe, not whether the old weighted blend can be nudged higher.
2. Put the next scientist effort into one of two lanes only: a controlled stacker-family variant on the existing OOF/test probabilities, or one new complementary prediction source that is structurally different enough to change the stack. Do not extend the current HistGBM third leg unless it first shows a meaningful standalone improvement.
3. Keep submissions tight. Submit only when the next candidate is either clearly above `0.971927` CV, or when the purpose is to test whether the stacking gain transfers to LB with acceptable calibration. Small cosmetic changes are not worth a slot.
4. Preserve one low-volume diversity lane, but require a credible ensemble path before investing more. Weak models are only useful now if they expose a gap in the current stack or provide a new basis for stacking.

## Refresh Triggers

- `S-089` is not reproducible on a fresh run or loses most of its advantage versus `S-083`.
- A new stacker or complementary model beats `0.971927` CV by a meaningful margin, or a submission proves the gain does not transfer.
- CV/LB divergence worsens beyond the established sub-0.003 band.
- The date changes again without a new leaderboard signal.
