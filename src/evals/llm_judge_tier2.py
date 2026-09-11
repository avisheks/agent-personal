"""
Tier 2: LLM-judge evaluation of super-agent sessions.

Constructs a fixed rubric from the constitution's llm_judge rules, calls the
LLM once, and returns structured scores. The rubric is deterministically
built from constitution.yaml — same version always produces the same prompt.
Called by evaluate.py.
"""

import json
import sys

try:
    import boto3
except ImportError:
    boto3 = None


def build_rubric_prompt(
    tier2_deferred: list[dict],
    events: list[dict],
    tier1_results: list[dict],
    catalog: dict,
) -> str:
    """Construct the fixed LLM-judge prompt from Tier 2 rules."""
    if not tier2_deferred:
        return ""

    events_summary = json.dumps(events, indent=2)
    tier1_summary = json.dumps(tier1_results, indent=2)
    catalog_summary = json.dumps(
        {sid: {"name": s["name"], "commands": s.get("commands", []),
               "triggers": s.get("triggers", [])}
         for sid, s in catalog.items()},
        indent=2,
    )

    rubric_sections = []
    for rule_info in tier2_deferred:
        rubric_sections.append(
            f"### Rule {rule_info['rule']}: {rule_info['principle']}\n"
            f"**Dimension:** {rule_info['dimension']}\n"
            f"**Severity:** {rule_info['severity']}\n"
            f"**Gap code if FAIL:** {rule_info.get('fail_maps_to', 'N/A')}\n\n"
            f"{rule_info['rubric']}\n"
        )

    rubric_block = "\n---\n".join(rubric_sections)

    return f"""You are an evaluation judge for an AI orchestrator agent. Your job is to score
the agent's performance on specific quality dimensions using a fixed rubric.

## Instructions

1. Read the session events (the full execution trace).
2. Read the Tier 1 deterministic evaluation results (already completed — do not re-evaluate those rules).
3. For each Tier 2 rule below, produce a verdict: PASS, MINOR, FAIL, or SKIP.
4. For each verdict, provide a one-sentence evidence statement citing specific events.
5. Return your response as a JSON object with the exact schema shown at the end.

## Skills Catalog (for reference)

{catalog_summary}

## Session Events

{events_summary}

## Tier 1 Results (already evaluated — for context only)

{tier1_summary}

## Tier 2 Rules to Evaluate

{rubric_block}

## Required Output Schema

Return ONLY a JSON object with this exact structure (no markdown, no explanation outside the JSON):

{{
  "tier2_results": [
    {{
      "rule": "<rule_id>",
      "verdict": "PASS | MINOR | FAIL | SKIP",
      "evidence": "<one-sentence justification citing specific event data>",
      "gap": "<gap code if FAIL, else null>"
    }}
  ]
}}

Produce one entry per Tier 2 rule listed above. Use SKIP only when the rule's
precondition does not apply to this session (e.g., no escalations occurred for
the escalation quality rule)."""


def call_llm(prompt: str, model_id: str, region: str, profile: str) -> dict:
    """Call Bedrock with the rubric prompt and parse the JSON response."""
    if boto3 is None:
        print("ERROR: boto3 not installed. Install with: pip install boto3", file=sys.stderr)
        sys.exit(1)

    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("bedrock-runtime")

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 4096, "temperature": 0.0},
    )

    text = response["output"]["message"]["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[: text.rfind("```")]

    return json.loads(text)


def run_tier2(
    tier2_deferred: list[dict],
    events: list[dict],
    tier1_results: list[dict],
    catalog: dict,
    model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
    region: str = "us-west-2",
    profile: str = "default",
    dry_run: bool = False,
) -> list[dict] | str:
    """
    Run Tier 2 LLM-judge evaluation.

    Returns list of result dicts, or the prompt string if dry_run=True.
    """
    prompt = build_rubric_prompt(tier2_deferred, events, tier1_results, catalog)
    if not prompt:
        return []

    if dry_run:
        return prompt

    llm_response = call_llm(prompt, model_id, region, profile)
    return llm_response.get("tier2_results", [])
