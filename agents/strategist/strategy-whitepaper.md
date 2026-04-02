# Strategy Whitepaper

## Current Date
April 2, 2026

## Deadline Assumption
April 30, 2026 — last calendar day of the competition month (S6E4 default assumption).

## Days Remaining
28

## Read

**Run pace and coverage:**
- 24 experiments completed in 1.5 days at ~16 runs/day throughput.
- Preprocessing, feature engineering, and five major model families (LR, RF, LGBM, HistGBM, XGB, CatBoost) have all been tested.
- Analyst performed three sessions covering class imbalance, interaction discovery, and fold stability analysis.
- Two leaderboard submissions executed; both scored with excellent CV/LB alignment (±0.003).

**Current position:**
- S-014 (XGBoost depth=5, subsample/colsample=0.8, StandardScaler+PolynomialFeatures, SM²) is a strong local optimum.
  - CV: 0.9709, LB: 0.9682 (rank 86, -0.0027 CV/LB delta)
  - Fold stability exceptional: std=0.0006, range 0.9699–0.9717
  - High-class recall 95.0% (19,959 TP / 21,009 High samples); improvement from baseline 5.5%
- Recent experiments (S-020–S-024) all underperformed S-014.
- Every feature engineering and regularization deviation tested so far has hurt CV.

**Signal quality:**
- CV/LB correlation is strong (both submissions within 0.003 delta).
- Fold stability is excellent; no evidence of leakage or overfitting.
- Analyst knowledge confirms SM² polynomial captures the key decision boundary (Soil_Moisture non-linearity and SM×Rainfall/Temperature interactions).

**The plateau:**
- Last 5 experiments all regressed from S-014 baseline.
- Current lane (incremental feature engineering / regularization tweaks) is exhausted.
- High-class recall is already exceptional (95%), leaving little room for class-balance micro-tuning.

## Emphasis

**Primary: Diversity and Ensemble Foundation (50%)**
- S-014 is not a final solution; it is a strong anchor for week-1 foundation.
- The supervisor should now build a short list of **structurally different models** using S-014's SM² feature set as the common input.
- Goal: Create 3–4 diverse branches (e.g., LightGBM aggressive tuning, linear SVM with engineered features, shallow neural net) that are meaningfully different from XGBoost in architecture, not just hyperparameters.
- These branches should score competitively with S-014 (within 0.003 CV), not beat it on CV alone.
- The diversity will unlock ensembling gains in week 2.

**Secondary: Targeted Model Architecture Exploration (30%)**
- Test **linear SVM with polynomial SM² features**: captures non-linear boundaries without tree-based splitting; adds a linear + kernel perspective orthogonal to boosting.
- Test **LightGBM with aggressive early stopping and higher learning rate**: different regularization philosophy than XGBoost; may discover alternate decision paths.
- Test **shallow neural net (2–3 layers, small width)** trained on StandardScaler + PolynomialFeatures: captures non-linearity via learned weights rather than ensemble of trees.
- Do not chase CV improvement in this lane; instead, measure **feature importance disagreement** and **fold-level prediction disagreement** with S-014.

**Background: Fold-Specific and Subgroup Tuning (15%)**
- S-014 shows very small subgroup gaps (East region -0.8%, Rabi season -0.4%, per-crop <1% variance).
- These gaps are so small they likely reflect data distribution, not model weakness.
- Keep this in reserve for week 2 only if ensemble gains plateau and major refinements are needed.

**Hold: Further Feature Engineering in Current Lane (0%)**
- Do not add more hand-crafted features to the SM² + polynomial base.
- The analyst identified the two strongest interactions (SM×Rainfall, SM×Temperature) and crop-specific modulation (Maize/Sugarcane).
- All additional feature engineering attempts have hurt CV.
- If feature engineering is revisited in week 2, it should be model-agnostic (e.g., target encoding, automated feature selection) paired with a different model family.

## Guidance For The Supervisor

### 1. **Accept S-014 as the Week-1 Anchor; Do Not Deepen Further in XGBoost Tuning**

S-014 is a strong local optimum with excellent fold stability, high-class recall (95%), and proven CV/LB correlation. Every attempt to improve it via additional feature engineering or regularization has failed. The supervisor should **stop iterating on XGBoost tuning and feature engineering now**.

This is the correct moment to pivot because:
- The marginal return on tuning the same model is negative (last 5 runs all regressed).
- Fold stability is so tight (std=0.0006) that further micro-tuning is unlikely to help.
- The plateau signal is clear and consistent.
- Time is abundant (28 days remain), so breadth-first exploration is the right strategy.

### 2. **Build a Diversity Shortlist: Three Structurally Different Models**

Over the next 3–5 experiments, create a short list of **structurally different candidate models** that all use S-014's SM² + StandardScaler + PolynomialFeatures preprocessing as input. Target:

- **Candidate A: Linear SVM with polynomial features** (adds a non-tree-based, kernel-based perspective)
- **Candidate B: LightGBM with aggressive tuning** (different regularization path: higher lr, early stop, feature bagging orthogonal to XGBoost's subsample strategy)
- **Candidate C: Shallow MLP** (learned non-linearity via neural weights, not tree splits)

Success criteria for candidates:
- CV score within 0.002–0.005 of S-014 (0.968–0.9703 acceptable).
- High-class recall >90% (accept some recall loss; precision trade-off is ok).
- **Feature importance / prediction disagreement with S-014**: measure correlation of predictions on OOF set; target <0.97 correlation (meaningful divergence).

Do not try to beat S-014 on CV. The goal is **diversity**, not improvement. Diverse weak models blend better than homogeneous ones.

### 3. **Then: Brief Ensemble Scan (Week 1 Tail); Commit to Ensembling Infrastructure in Week 2**

Once the diversity shortlist is locked (likely by April 4–5, end of week 1):
- Run 1–2 simple ensemble experiments (average, rank average) on the shortlist to confirm ensemble gains are possible.
- Measure: does the best 3-model ensemble beat S-014's 0.9682 LB score?
- If yes: submit one ensemble by end of week 1 to extract leaderboard signal.
- If no: do not submit; instead, use week 2 to build more diverse branches (alternate seeds, alternate preprocessing paths).

### 4. **When to Call Week 1 Complete and Pivot to Week 2**

Week 1 ends when:
- ✓ S-014 is locked as the anchor (done).
- ✓ 3–4 structurally different models are tested and ranked by diversity (target: April 4–5).
- ✓ One test ensemble is completed (target: April 5).
- ✓ Decision made: continue ensemble refinement vs. build more diversity (target: April 5).

If ensemble gains (ΔCV > +0.0005) appear possible, move directly to week 2 ensembling lane. If ensemble gains are negligible, extend diversity building (add 1–2 more model families or alternate seeds) before committing to ensembling.

### 5. **Revised Week 1–2 Emphasis (Departure from Default Lifecycle)**

Default lifecycle for week 1 is 70% EDA, 25% base models, 5% refinement. This run is deviating because:
- EDA is nearly complete (analyst identified key interactions; no distributional shift, no leakage).
- Base models have already been thoroughly tested (5 families explored).
- The supervisor is now shifting to diversity-first ensembling foundation, skipping incremental refinement.

**Revised week-1 emphasis (April 1–7):**
- 15% EDA (maintain: if any subgroup analysis gaps emerge, close them).
- 35% base models (shift: lock the anchor and build a diverse 3–4 model shortlist).
- 40% ensemble foundation (shift: test blending strategies early, even if weak).
- 10% moonshots (hold: defer pseudo-labeling, specialist models until week 3).

This front-loads ensemble diversity work and compresses the traditional refinement phase into week 2, where it is more useful (e.g., stacking, weighted blending, seed bagging).

## Refresh Triggers

- **Analyst request:** if subgroup performance gaps (East region, Rabi season, or crop-specific) appear larger than expected in a new candidate model, request fold-level analysis before deciding to add subgroup-specific features.
- **Ensemble signal:** if the first ensemble test shows a >0.0010 CV gain over S-014, confirm leaderboard submission will be worth using one of week 1's 5 submissions. If gain is <0.0003, defer submission to week 2.
- **Diversity plateau:** if the first 3 candidate models all score within 0.001 CV of each other and disagree <0.85 in OOF predictions, the diversity shortlist is too homogeneous. Request a fundamentally different approach (e.g., multi-layer MLP, linear SVM with hand-tuned kernel).
- **Unexpected regression:** if a candidate model scores >0.005 below S-014 CV with no meaningful diversity gain (>0.95 correlation to S-014 OOF), discard it and try the next architecture immediately.
