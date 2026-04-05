import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from harness import supervisor_snapshot


class SupervisorSnapshotTests(unittest.TestCase):
    def test_load_experiments_keeps_scored_and_pending_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_dir = root / "history"
            history_dir.mkdir(parents=True)
            (history_dir / "experiments.md").write_text(
                "# Experiments\n\n"
                "| task_id | finished_at | lane | metric | delta_best | status | artifact_dir | summary |\n"
                "|---------|-------------|------|--------|------------|--------|--------------|---------|\n"
                "| S-001 | 2026-04-01T09:00Z | base | 0.910000 | +0.000000 | scored | artifacts/S-001 | baseline |\n"
                "| S-002 | 2026-04-01T10:00Z | base | pending | pending | timeout | artifacts/S-002 | timed out |\n"
            )

            with mock.patch.object(supervisor_snapshot, "REPO_ROOT", root):
                rows = supervisor_snapshot._load_experiments()

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0].task_id, "S-001")
            self.assertAlmostEqual(rows[0].cv or 0.0, 0.91)
            self.assertIsNone(rows[1].cv)
            self.assertEqual(rows[1].summary, "timed out")

    def test_main_writes_compact_run_state_without_copying_evidence_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_repo_fixture(root)

            output_path = root / "state/run-state.md"
            with mock.patch.object(supervisor_snapshot, "REPO_ROOT", root), mock.patch.object(
                sys,
                "argv",
                [
                    "supervisor_snapshot",
                    "--output-path",
                    str(output_path),
                ],
            ):
                supervisor_snapshot.main()

            rendered = output_path.read_text()
            self.assertIn("stage: promotion_gate", rendered)
            self.assertIn("lane: S-094-successor / Medium-stabilization", rendered)
            self.assertIn("active_scientist_task: S-012 | Try weighted blend", rendered)
            self.assertIn("active_analyst_task: A-002 | Does the blend add useful diversity?", rendered)
            self.assertIn(
                "- best_offline_candidate: S-011 | 0.972000 | weighted blend",
                rendered,
            )
            self.assertIn(
                "- best_submitted_candidate: S-014 | 2026-04-02T00:09Z | 0.96820 LB | rank 86",
                rendered,
            )
            self.assertIn("- next_decision: supported Does the blend add useful diversity?", rendered)
            self.assertIn("- next_batch: Re-run the anchor blend and compare OOF correlation.", rendered)
            self.assertNotIn("VERY LONG EVIDENCE BODY", rendered)

    def _write_repo_fixture(self, root: Path) -> None:
        (root / "state").mkdir(parents=True)
        (root / "history").mkdir(parents=True)

        (root / "state/run-state.md").write_text(
            "# Run State\n\n"
            "as_of: 2026-04-04\n"
            "stage: promotion_gate\n"
            "lane: S-094-successor / Medium-stabilization\n"
            "active_scientist_task: none\n"
            "active_analyst_task: none\n"
        )
        (root / "state/memory.md").write_text(
            "# Memory\n\n"
            "- Promotion gate on the S-094 successor lane.\n"
        )
        (root / "state/scientist-task.md").write_text(
            "# Active Scientist Task\n"
            "status: active\n"
            "id: S-012\n"
            "batch_goal: Try weighted blend\n"
        )
        (root / "state/analyst-task.md").write_text(
            "# Active Analyst Task\n"
            "status: active\n"
            "id: A-002\n"
            "q: Does the blend add useful diversity?\n"
        )

        (root / "history/experiments.md").write_text(
            "# Experiments\n\n"
            "| task_id | finished_at | lane | metric | delta_best | status | artifact_dir | summary |\n"
            "|---------|-------------|------|--------|------------|--------|--------------|---------|\n"
            "| S-010 | 2026-04-01T08:30Z | S-094-successor / Medium-stabilization | 0.970000 | +0.000000 | scored | artifacts/S-010 | xgb baseline |\n"
            "| S-011 | 2026-04-01T12:00Z | S-094-successor / Medium-stabilization | 0.972000 | +0.002000 | scored | artifacts/S-011 | weighted blend |\n"
            "| S-012 | 2026-04-01T14:00Z | S-094-successor / Medium-stabilization | pending | pending | running | artifacts/S-012 | blocked |\n"
        )
        (root / "history/analyses.md").write_text(
            "# Analyses\n\n"
            "| analysis_id | at | q | verdict | confidence | artifact_dir | summary |\n"
            "|-------------|----|---|---------|------------|--------------|---------|\n"
            "| A-002 | 2026-04-02T10:00Z | Does the blend add useful diversity? | supported | high | artifacts/A-002 | Re-run the anchor blend and compare OOF correlation. |\n\n"
            "VERY LONG EVIDENCE BODY\n"
        )
        (root / "history/submissions.md").write_text(
            "# Submissions\n\n"
            "| task_id | submitted_at | cv_score | lb_score | lb_rank | status | summary |\n"
            "|---------|--------------|----------|----------|---------|--------|---------|\n"
            "| S-014 | 2026-04-02T00:09Z | 0.970856 | 0.96820 | 86 | scored | tuned xgb |\n"
        )


if __name__ == "__main__":
    unittest.main()
