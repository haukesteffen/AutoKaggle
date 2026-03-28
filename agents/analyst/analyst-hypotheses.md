# Active Hypothesis

**Hypothesis:** Within the Month-to-month × Fiber optic subgroup, does churn rate show a non-linear threshold effect by tenure — specifically, does churn drop sharply at or after 12 months or 24 months, suggesting a binned interaction is more informative than a simple binary flag?

**Decision if supported (clear threshold exists):** Direct the scientist to use a binned tenure × mtm_fiber interaction (e.g. `mtm_fiber_0_12m`, `mtm_fiber_13_24m`, `mtm_fiber_25plus`) rather than a single binary flag. The bin boundaries should match where churn drops.

**Decision if rejected (churn declines gradually, no clear step):** A single `mtm_fiber` binary flag is sufficient. No need for tenure bins within the subgroup — the simpler feature is fine.

**Allowed evidence:** churn rate by tenure month or tenure bin within the Month-to-month × Fiber optic subgroup only. Counts and rates in a table. No plots.

**Relevant data:** `/Users/hs/dev/AutoKaggle/data/train.csv`
