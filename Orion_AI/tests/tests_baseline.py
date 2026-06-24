"""
Characterization tests for Orion v0.1.

These capture CURRENT behavior before Phase 1 migration.
They are not correctness tests — they are sameness tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


PROJECT_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "Orion_AI").exists()
)

sys.path.insert(0, str(PROJECT_ROOT / "Orion_AI"))

from Core.Agent.orchestrator import Orchestrator
from skills.response_synthesizer import build_prompt_with_context


def make_orchestrator_without_init():
    agent = Orchestrator.__new__(Orchestrator)
    agent.llm = MagicMock()
    agent.memory = []
    agent.skills = {}
    return agent


def test_decide_skills_with_valid_json():
    agent = make_orchestrator_without_init()
    agent.llm.generate.return_value = '{"skills": ["web_search"], "reason": "test"}'

    decision = agent._decide_skills("any query")

    assert decision["skills"] == ["web_search"]
    assert decision["reason"] == "test"


def test_decide_skills_with_malformed_json_falls_back_to_web_search():
    agent = make_orchestrator_without_init()
    agent.llm.generate.return_value = "not json at all"

    decision = agent._decide_skills("any query")

    assert decision == {
        "skills": ["web_search"],
        "reason": "classifier failed to parse JSON",
    }


def test_decide_skills_with_unknown_skill_name_drops_unknown_skill():
    agent = make_orchestrator_without_init()
    agent.llm.generate.return_value = '{"skills": ["nonexistent"], "reason": "x"}'

    decision = agent._decide_skills("any query")

    assert decision == {
        "skills": [],
        "reason": "x",
    }


def test_run_with_empty_skills_uses_empty_results_and_fallback_prompt_path():
    agent = make_orchestrator_without_init()
    agent.llm.generate.return_value = "final answer"

    with patch.object(
        agent,
        "_decide_skills",
        return_value={"skills": [], "reason": "none"},
    ):
        with patch(
            "Core.Agent.orchestrator.build_prompt_with_context",
            return_value="fallback prompt",
        ) as mock_prompt_builder:
            result = agent.run("test query")

    assert result == "final answer"
    mock_prompt_builder.assert_called_once_with("test query", [])
    agent.llm.generate.assert_called_once_with("fallback prompt")
    assert agent.memory == [
        {"role": "user", "content": "test query"},
        {"role": "assistant", "content": "final answer"},
    ]


def test_skill_crash_produces_contract_compliant_failure_dict():
    agent = make_orchestrator_without_init()
    agent.llm.generate.return_value = "final answer"

    def crashing_skill(query):
        raise Exception("boom")

    agent.skills = {
        "crashing_skill": crashing_skill,
    }

    captured_results = {}

    def capture_prompt(query, results):
        captured_results["query"] = query
        captured_results["results"] = results
        return "prompt after crash"

    with patch.object(
        agent,
        "_decide_skills",
        return_value={"skills": ["crashing_skill"], "reason": "test crash"},
    ):
        with patch(
            "Core.Agent.orchestrator.build_prompt_with_context",
            side_effect=capture_prompt,
        ):
            result = agent.run("test query")

    assert result == "final answer"
    assert captured_results["query"] == "test query"
    assert captured_results["results"] == [
        {
            "skill": "crashing_skill",
            "success": False,
            "data": None,
            "error": "boom",
        }
    ]


def test_build_prompt_with_context_with_no_successful_skills_uses_fallback_prompt():
    prompt = build_prompt_with_context("What is recursion?", [])

    assert "You are Orion, a helpful research assistant." in prompt
    assert "Answer the following question as accurately as possible." in prompt
    assert "Question: What is recursion?" in prompt
    assert "--- WEB_SEARCH RESULTS ---" not in prompt


def test_build_prompt_with_context_with_one_successful_skill_includes_context_section():
    skill_results = [
        {
            "skill": "web_search",
            "success": True,
            "data": "[1] Example result\n    Source: https://example.com",
            "error": None,
        }
    ]

    prompt = build_prompt_with_context("latest AI news", skill_results)

    assert "You are Orion, an AI research assistant with access to tool outputs." in prompt
    assert "--- WEB_SEARCH RESULTS ---" in prompt
    assert "[1] Example result" in prompt
    assert "Source: https://example.com" in prompt
    assert "--- END WEB_SEARCH ---" in prompt
    assert "User Question: latest AI news" in prompt