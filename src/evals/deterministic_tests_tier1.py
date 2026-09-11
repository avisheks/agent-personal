"""
Tier 1: Deterministic rule-based evaluation of super-agent sessions.

Runs all 'tier: deterministic' rules from the constitution against a session's
events. Each rule produces PASS/FAIL/SKIP + evidence. Called by evaluate.py.
"""

import json
from collections import defaultdict


def get_event(events: list[dict], event_type: str) -> dict | None:
    for e in events:
        if e["event"] == event_type:
            return e
    return None


def get_events(events: list[dict], event_type: str) -> list[dict]:
    return [e for e in events if e["event"] == event_type]


def get_approved_skills(events: list[dict]) -> set[str]:
    approved = set()
    pr = get_event(events, "plan_response")
    if pr and pr.get("action") in ("approved", "auto_approved"):
        pp = get_event(events, "plan_presented")
        if pp:
            for step in pp.get("plan_steps", []):
                approved.add(step.get("skill", ""))
    for esc in get_events(events, "escalation"):
        if esc.get("user_response") == "approved":
            approved.add(esc.get("skill", ""))
    return approved


def query_trigger_matches(query: str, catalog: dict) -> dict[str, list[str]]:
    matches = {}
    query_lower = query.lower()
    for skill_id, skill in catalog.items():
        hits = [t for t in skill.get("triggers", []) if t.lower() in query_lower]
        if hits:
            matches[skill_id] = hits
    return matches


# ── Rule Checkers ─────────────────────────────────────────────────


def check_e1(events, rule, catalog):
    ss = get_event(events, "session_start")
    se = get_events(events, "step_execution")
    query_ev = get_event(events, "query")
    if not ss or not se:
        return "SKIP", "No session_start or no step_execution events"
    complexity = query_ev.get("complexity", "medium") if query_ev else "medium"
    threshold = rule["check"]["thresholds"].get(complexity, 3)
    turns = min(e["turn"] for e in se) - ss["turn"]
    if turns <= threshold:
        return "PASS", f"turns_to_first_execution={turns}, threshold={threshold} ({complexity})"
    return "FAIL", f"turns_to_first_execution={turns}, threshold={threshold} ({complexity})"


def check_e2(events, rule, catalog):
    interp = get_event(events, "interpretation")
    if not interp:
        return "SKIP", "No interpretation event"
    clarified = interp.get("clarification_needed", False)
    ambiguous = interp.get("ambiguous", False)
    if clarified and not ambiguous:
        return "FAIL", f"clarification_needed={clarified}, ambiguous={ambiguous}"
    return "PASS", f"clarification_needed={clarified}, ambiguous={ambiguous}"


def check_e3(events, rule, catalog):
    pp = get_event(events, "plan_presented")
    pr = get_event(events, "plan_response")
    interp = get_event(events, "interpretation")
    if not pp or not pr:
        return "SKIP", "No plan_presented or plan_response"
    single_step = len(pp.get("plan_steps", [])) == 1
    ambiguous = interp.get("ambiguous", True) if interp else True
    action = pr.get("action", "")
    if single_step and not ambiguous and action != "auto_approved":
        return "FAIL", f"single_step={single_step}, ambiguous={ambiguous}, action={action}"
    return "PASS", f"single_step={single_step}, ambiguous={ambiguous}, action={action}"


def check_r1(events, rule, catalog):
    ss = get_event(events, "skill_selection")
    query_ev = get_event(events, "query")
    if not ss or not query_ev:
        return "SKIP", "No skill_selection or query event"
    trigger_map = query_trigger_matches(query_ev.get("query", ""), catalog)
    selected = ss.get("selected", [])
    uncovered = [s for s in selected if s not in trigger_map]
    if uncovered:
        return "FAIL", f"Selected skills with no trigger match: {uncovered}"
    return "PASS", f"All {len(selected)} selected skills have trigger matches"


def check_r2(events, rule, catalog):
    ss = get_event(events, "skill_selection")
    query_ev = get_event(events, "query")
    if not ss or not query_ev:
        return "SKIP", "No skill_selection or query event"
    trigger_map = query_trigger_matches(query_ev.get("query", ""), catalog)
    selected = set(ss.get("selected", []))
    considered = {c["id"] for c in ss.get("considered", []) if "id" in c}
    known = selected | considered
    min_hits = rule["check"].get("min_trigger_hits", 2)
    blind = {sid: hits for sid, hits in trigger_map.items()
             if len(hits) >= min_hits and sid not in known}
    if blind:
        return "FAIL", f"Unconsidered skills with strong trigger signal: {dict(blind)}"
    return "PASS", f"No blind spots (min_hits={min_hits})"


def check_r3(events, rule, catalog):
    ss = get_event(events, "skill_selection")
    if not ss:
        return "SKIP", "No skill_selection event"
    considered = ss.get("considered", [])
    if not considered:
        return "SKIP", "No skills were considered and rejected"
    empty = [c.get("id", "?") for c in considered if not c.get("rejected_reason")]
    if empty:
        return "FAIL", f"Skills with empty rejection reason: {empty}"
    return "PASS", f"All {len(considered)} rejections have reasons"


def check_r4(events, rule, catalog):
    pp = get_event(events, "plan_presented")
    query_ev = get_event(events, "query")
    if not pp or not query_ev:
        return "SKIP", "No plan_presented or query event"
    steps = len(pp.get("plan_steps", []))
    intents = query_ev.get("intent_count", 1)
    over = rule["check"].get("over_decompose_threshold", 1.5)
    under = rule["check"].get("under_decompose_threshold", 1.0)
    if steps > intents * over:
        return "FAIL", f"Over-decomposed: {steps} steps for {intents} intents (threshold: {intents * over})"
    if steps < intents * under:
        return "FAIL", f"Under-decomposed: {steps} steps for {intents} intents"
    return "PASS", f"steps={steps}, intents={intents}, ratio={steps/intents:.1f}"


def check_p1(events, rule, catalog):
    pr = get_event(events, "plan_response")
    execs = get_events(events, "step_execution")
    if not execs:
        return "SKIP", "No step_execution events"
    if not pr:
        return "FAIL", "step_execution exists but no plan_response"
    pr_ts = pr.get("ts", "")
    early = [e for e in execs if e.get("ts", "") < pr_ts]
    if early:
        return "FAIL", f"{len(early)} step(s) executed before plan_response"
    return "PASS", "All executions after approval"


def check_p2(events, rule, catalog):
    approved = get_approved_skills(events)
    execs = get_events(events, "step_execution")
    if not execs:
        return "SKIP", "No step_execution events"
    unapproved = [e["skill"] for e in execs if e.get("skill") not in approved]
    if unapproved:
        return "FAIL", f"Unapproved skills executed: {unapproved}"
    return "PASS", f"All executed skills in approved set: {approved}"


def check_p3(events, rule, catalog):
    followups = get_events(events, "followup")
    new_skill_followups = [f for f in followups if f.get("type") == "new_skill"]
    if not new_skill_followups:
        return "SKIP", "No new_skill followups"
    escalated_skills = {e["skill"] for e in get_events(events, "escalation")
                        if e.get("user_response") == "approved"}
    missing = [f["skill_used"] for f in new_skill_followups
               if f.get("skill_used") not in escalated_skills]
    if missing:
        return "FAIL", f"New skills used in followup without escalation: {missing}"
    return "PASS", "All new-skill followups have prior escalation"


def check_p4(events, rule, catalog):
    has_start = get_event(events, "session_start") is not None
    has_end = get_event(events, "session_end") is not None
    if has_start and has_end:
        return "PASS", "Both bookends present"
    missing = []
    if not has_start:
        missing.append("session_start")
    if not has_end:
        missing.append("session_end")
    return "FAIL", f"Missing: {', '.join(missing)}"


def check_q1(events, rule, catalog):
    ss = get_event(events, "skill_selection")
    pc = get_event(events, "prerequisite_check")
    if not ss:
        return "SKIP", "No skill_selection event"
    selected = ss.get("selected", [])
    config_skills = [s for s in selected if catalog.get(s, {}).get("requires_config")]
    if not config_skills:
        return "SKIP", "No selected skills require config"
    if not pc:
        return "FAIL", f"Config-requiring skills {config_skills} but no prerequisite_check event"
    checked_skills = {c.get("skill") for c in pc.get("checks", [])
                      if "config" in c.get("item", "").lower()}
    unchecked = [s for s in config_skills if s not in checked_skills]
    if unchecked:
        return "FAIL", f"Config-requiring skills without config check: {unchecked}"
    return "PASS", f"All config-requiring skills checked: {config_skills}"


def check_q2(events, rule, catalog):
    pc = get_event(events, "prerequisite_check")
    pp = get_event(events, "plan_presented")
    if not pc:
        return "SKIP", "No prerequisite_check event"
    unknowns = [c for c in pc.get("checks", []) if c.get("status") == "unknown"]
    if not unknowns:
        return "PASS", "No unknown prerequisites"
    plan_text = json.dumps(pp) if pp else ""
    unflagged = [u for u in unknowns
                 if u.get("item", "???") not in plan_text and u.get("skill", "???") not in plan_text]
    if unflagged:
        items = [f"{u.get('skill')}:{u.get('item')}" for u in unflagged]
        return "FAIL", f"Unknown prereqs not flagged in plan: {items}"
    return "PASS", f"{len(unknowns)} unknown prereqs all flagged in plan"


def check_c1(events, rule, catalog):
    pp = get_event(events, "plan_presented")
    execs = get_events(events, "step_execution")
    if not pp:
        return "SKIP", "No plan_presented event"
    planned_steps = {s.get("step") for s in pp.get("plan_steps", [])}
    executed_steps = {e.get("step") for e in execs}
    missing = planned_steps - executed_steps
    if missing:
        return "FAIL", f"Planned steps not executed: {missing}"
    return "PASS", f"All {len(planned_steps)} planned steps executed"


def check_c2(events, rule, catalog):
    execs = get_events(events, "step_execution")
    errors = get_events(events, "error")
    failed = [e for e in execs if e.get("status") == "failed"]
    if not failed:
        return "SKIP", "No failed steps"
    if not errors:
        return "FAIL", f"{len(failed)} failed step(s) with no error events at all"
    error_details = {e.get("detail", "") for e in errors}
    silent = [f for f in failed if not any(
        f.get("skill", "") in d or f.get("command", "") in d for d in error_details)]
    if silent:
        return "FAIL", f"{len(silent)} failed step(s) with no matching error event"
    return "PASS", f"All {len(failed)} failed steps have error events"


def check_c3(events, rule, catalog):
    se = get_event(events, "session_end")
    if not se:
        return "SKIP", "No session_end event"
    required = ["total_turns", "steps_completed", "steps_failed"]
    missing = [f for f in required if f not in se]
    if missing:
        return "FAIL", f"session_end missing fields: {missing}"
    return "PASS", "All summary fields present"


RULE_CHECKERS = {
    "E1": check_e1, "E2": check_e2, "E3": check_e3,
    "R1": check_r1, "R2": check_r2, "R3": check_r3, "R4": check_r4,
    "P1": check_p1, "P2": check_p2, "P3": check_p3, "P4": check_p4,
    "Q1": check_q1, "Q2": check_q2,
    "C1": check_c1, "C2": check_c2, "C3": check_c3,
}


def run_tier1(
    events: list[dict],
    constitution: dict,
    catalog: dict,
) -> tuple[list[dict], list[dict]]:
    """
    Run all deterministic rules. Returns (tier1_results, tier2_deferred).
    """
    results = []
    tier2_deferred = []

    for rule in constitution["principles"]:
        rule_id = rule["id"]
        tier = rule["tier"]

        if tier == "llm_judge":
            tier2_deferred.append({
                "rule": rule_id,
                "principle": rule["principle"],
                "dimension": rule["dimension"],
                "rubric": rule.get("rubric", ""),
                "fail_maps_to": rule.get("fail_maps_to"),
                "severity": rule["severity"],
            })
            continue

        checker = RULE_CHECKERS.get(rule_id)
        if not checker:
            results.append({
                "rule": rule_id,
                "verdict": "SKIP",
                "evidence": f"No checker implemented for {rule_id}",
            })
            continue

        verdict, evidence = checker(events, rule, catalog)
        entry = {
            "rule": rule_id,
            "dimension": rule["dimension"],
            "verdict": verdict,
            "evidence": evidence,
            "severity": rule["severity"],
        }
        if verdict == "FAIL" and rule.get("fail_maps_to"):
            entry["gap"] = rule["fail_maps_to"]
        results.append(entry)

    return results, tier2_deferred
