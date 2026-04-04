import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from harness import supervisor_snapshot


class SupervisorSnapshotTests(unittest.TestCase):
    def test_parse_scientist_results_keeps_scored_and_non_scored_rows(self) -> None:
        text = (
            "# Scientist Results\n\n"
            "| id | score | std | delta_best | desc |\n"
            "|----|-------|-----|------------|------|\n"
            "| S-001 | 0.910000 | 0.010000 | +0.000000 | baseline |\n"
            "| S-002 | - | - | - | timed out |\n"
        )

        rows = supervisor_snapshot.parse_scientist_results(text)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].task_id, "S-001")
        self.assertAlmostEqual(rows[0].score or 0.0, 0.91)
        self.assertIsNone(rows[1].score)
        self.assertEqual(rows[1].desc, "timed out")

    def test_main_writes_compact_run_state_without_copying_evidence_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_repo_fixture(root)

            output_path = root / "agents/supervisor/run-state.md"
            with mock.patch.object(supervisor_snapshot, "REPO_ROOT", root), mock.patch.object(
                sys,
                "argv",
                [
                    "supervisor_snapshot",
                    "--output-path",
                    str(output_path),
                    "--max-recent-results",
                    "2",
                    "--max-recent-knowledge",
                    "2",
                    "--max-recent-findings",
                    "1",
                ],
            ):
                supervisor_snapshot.main()

            rendered = output_path.read_text()
            self.assertIn("best_cv: 0.972000 (S-011)", rendered)
            self.assertIn("active_scientist_task: S-012 | Try weighted blend", rendered)
            self.assertIn("AK-002 | Blend diversity matters", rendered)
            self.assertIn("A-002 | verdict=supported | conf=high", rendered)
            self.assertIn("best_lb: 0.96820 (S-014) | rank 86", rendered)
            self.assertNotIn("VERY LONG EVIDENCE BODY", rendered)

    def _write_repo_fixture(self, root: Path) -> None:
        (root / "agents/scientist").mkdir(parents=True)
        (root / "agents/analyst").mkdir(parents=True)
        (root / "agents/strategist").mkdir(parents=True)
        (root / "agents/supervisor").mkdir(parents=True)

        (root / "agents/scientist/scientist-results.md").write_text(
            "# Scientist Results\n\n"
            "| id | score | std | delta_best | desc |\n"
            "|----|-------|-----|------------|------|\n"
            "| S-010 | 0.970000 | 0.001000 | +0.000000 | xgb baseline |\n"
            "| S-011 | 0.972000 | 0.001200 | +0.002000 | weighted blend |\n"
            "| S-012 | - | - | - | blocked |\n"
        )

        (root / "agents/analyst/analyst-knowledge.md").write_text(
            "# Analyst Knowledge\n\n"
            "## AK-001 — SM2 is durable\n"
            "source: A-001\n"
            "at: 2026-04-01\n\n"
            "- Soil moisture non-linearity is real.\n\n"
            "## AK-002 — Blend diversity matters\n"
            "source: A-002\n"
            "at: 2026-04-02\n\n"
            "- OOF correlation is the key ensemble signal.\n"
        )

        (root / "agents/analyst/analyst-findings.md").write_text(
            "# Analyst Findings\n\n"
            "## A-002\n"
            "at: 2026-04-02T10:00Z\n"
            "q: Does the blend add useful diversity?\n"
            "verdict: supported\n"
            "conf: high\n"
            "evidence:\n"
            "VERY LONG EVIDENCE BODY\n"
        )

        (root / "agents/strategist/strategy-whitepaper.md").write_text(
            "# Strategy Whitepaper\n\n"
            "## Current Date\n"
            "April 4, 2026\n\n"
            "## Deadline Assumption\n"
            "April 30, 2026 — end of month.\n\n"
            "## Days Remaining\n"
            "26\n\n"
            "## Emphasis\n"
            "Primary: Lock ensemble anchor\n"
            "Secondary: Validate diversity\n"
            "Background: Minor subgroup checks\n"
            "Hold: New feature ideation\n\n"
            "## Guidance For The Supervisor\n"
            "1. Keep the best blend as the anchor.\n"
            "2. Avoid new feature churn.\n"
        )

        (root / "agents/supervisor/leaderboard-history.md").write_text(
            "# Leaderboard History\n\n"
            "## Submission Ledger\n\n"
            "| task_id | submitted_at | cv_score | status | lb_score | lb_rank | rationale |\n"
            "|---------|--------------|----------|--------|----------|---------|-----------|\n"
            "| S-014 | 2026-04-02T00:09Z | 0.970856 | scored | 0.96820 | 86 | tuned xgb |\n"
        )

        (root / "agents/strategist/strategy-request.md").write_text(
            "# Strategy Request\nstatus: none\n"
        )
        (root / "agents/scientist/scientist-task.md").write_text(
            "# Active Scientist Task\n"
            "status: active\n"
            "id: S-012\n"
            "goal: Try weighted blend\n"
        )
        (root / "agents/analyst/analyst-hypothesis.md").write_text(
            "# Active Analyst Hypothesis\nstatus: none\n"
        )


if __name__ == "__main__":
    unittest.main()
