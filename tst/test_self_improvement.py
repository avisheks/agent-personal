"""Tests for the self-improvement pipeline."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from self_improvement.capture import build_trajectory, save_trajectory
from self_improvement.feedback import log_feedback
from self_improvement.reflector import generate_reflection
from self_improvement.proposer import propose_improvements


class TestCapture:
    def test_build_trajectory_minimal(self):
        t = build_trajectory(skill="test-skill")
        assert t["skill"] == "test-skill"
        assert t["inputs"] == {}
        assert t["outputs"] == []
        assert t["errors"] == []
        assert t["feedback"] is None
        assert "timestamp" in t

    def test_build_trajectory_full(self):
        t = build_trajectory(
            skill="options-pnl",
            inputs={"input_dir": ".local/data"},
            outputs=["computed-pnl.json"],
            duration_sec=2.5,
            errors=[],
            feedback="looks good",
        )
        assert t["skill"] == "options-pnl"
        assert t["duration_sec"] == 2.5
        assert t["feedback"] == "looks good"

    def test_save_trajectory_creates_file(self, tmp_path):
        with patch("self_improvement.capture.MEMORY_DIR", tmp_path):
            t = build_trajectory(skill="test-skill", feedback="test")
            path = save_trajectory(t)
            assert path.exists()
            content = path.read_text().strip()
            data = json.loads(content)
            assert data["skill"] == "test-skill"


class TestFeedback:
    def test_log_feedback_creates_file(self, tmp_path):
        with patch("self_improvement.feedback.FEEDBACK_DIR", tmp_path):
            path = log_feedback(
                skill="tour-planner-v2",
                note="missed restaurant backup",
                feedback_type="bug",
            )
            assert path.exists()
            content = path.read_text().strip()
            data = json.loads(content)
            assert data["skill"] == "tour-planner-v2"
            assert data["type"] == "bug"


class TestReflector:
    def test_generate_reflection_empty(self):
        reflection = generate_reflection(
            skill="test", trajectories=[], feedback=[]
        )
        assert reflection["trajectory_count"] == 0
        assert reflection["feedback_count"] == 0
        assert reflection["error_rate"] == 0

    def test_generate_reflection_with_errors(self):
        trajectories = [
            {"skill": "test", "errors": ["parse failed"], "timestamp": "2026-01-01"},
            {"skill": "test", "errors": [], "timestamp": "2026-01-02"},
        ]
        feedback = [
            {"skill": "test", "type": "bug", "note": "wrong output"},
            {"skill": "test", "type": "praise", "note": "fast execution"},
        ]
        reflection = generate_reflection(
            skill="test", trajectories=trajectories, feedback=feedback
        )
        assert reflection["error_rate"] == 0.5
        assert "wrong output" in reflection["summary"]["fix"]
        assert "fast execution" in reflection["summary"]["keep"]


class TestProposer:
    def test_propose_from_reflection(self):
        reflection = {
            "timestamp": "2026-07-27T10:00:00+00:00",
            "skill": "options-pnl",
            "trajectory_count": 5,
            "feedback_count": 2,
            "summary": {
                "keep": ["accurate totals"],
                "fix": ["missed AMZN assignment"],
                "add": ["add weekly breakdown chart"],
            },
            "error_rate": 0.1,
            "skills_involved": ["options-pnl"],
        }
        proposals = propose_improvements(reflection)
        assert len(proposals) == 2
        assert proposals[0]["type"] == "fix"
        assert proposals[1]["type"] == "enhancement"
        assert all(p["status"] == "proposed" for p in proposals)
