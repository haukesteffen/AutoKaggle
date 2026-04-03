# Active Scientist Task
status: done
id: S-079
at: 2026-04-03T15:00Z
goal: Combine the two best MLP improvements: multi-seed ensemble (3 seeds: 42, 123, 456) + target encoding for cats (TargetEncoder cv=5) on poly3 top-4 feature set. MLPClassifier(hidden_layer_sizes=(64,32), activation='tanh', max_iter=500, early_stopping=True, validation_fraction=0.1, learning_rate_init=0.001). Feature set: poly3 top-4 (43 numeric), StandardScaler, TargetEncoder(cv=5) on 8 cats. For each fold: fit 3 pipelines (seeds 42, 123, 456), average predict_proba. compute_sample_weight('balanced', y_train). n_jobs=-1 in ColumnTransformer. Hypothesis: combining multi-seed averaging (S-073: +0.001 over S-065) with target encoding (S-071: +0.0006 over S-065) may push MLP to ~0.965+.
reference: result=S-071, result=S-073
