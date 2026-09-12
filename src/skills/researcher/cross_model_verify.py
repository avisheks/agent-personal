#!/usr/bin/env python3
"""Cross-model claim verification using GPT-OSS via AWS Bedrock.

Sends claims extracted by Claude to a DIFFERENT LLM for independent
verification, avoiding self-verification bias.
"""

import argparse
import json
import sys
import time

import boto3


BATCH_SIZE = 5
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds

SYSTEM_PROMPT = (
    "You are a fact-verification assistant. You will be given knowledge context "
    "and a list of claims. For each claim, determine whether it is SUPPORTED, "
    "CONTRADICTED, or UNVERIFIABLE based solely on the provided context.\n\n"
    "Respond with a JSON array. Each element must have:\n"
    '  - "id": the claim ID\n'
    '  - "verdict": one of "SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"\n'
    '  - "confidence": float 0.0-1.0\n'
    '  - "evidence": brief explanation referencing the context\n'
    '  - "suggested_correction": a corrected statement if CONTRADICTED, else null\n\n'
    "Return ONLY the JSON array, no markdown fences or extra text."
)


def build_user_prompt(kb_context: dict, claims_batch: list[dict]) -> str:
    """Build the user message with KB context and claims to verify."""
    context_parts = []
    if kb_context.get("knowledge_pages"):
        for i, page in enumerate(kb_context["knowledge_pages"], 1):
            context_parts.append(f"--- Knowledge Page {i} ---\n{page}")
    if kb_context.get("facts_manifest"):
        facts = "\n".join(
            f"- {f['entity']}.{f['attribute']} = {f['value']}"
            for f in kb_context["facts_manifest"]
        )
        context_parts.append(f"--- Facts Manifest ---\n{facts}")

    claims_text = "\n".join(
        f'- [{c["id"]}] (section: {c.get("section", "N/A")}): {c["text"]}'
        for c in claims_batch
    )

    return (
        f"Topic: {kb_context.get('topic', 'general')}\n\n"
        f"KNOWLEDGE CONTEXT:\n{''.join(context_parts)}\n\n"
        f"CLAIMS TO VERIFY:\n{claims_text}"
    )


def call_bedrock(client, model_id: str, kb_context: dict, claims_batch: list[dict]) -> list[dict]:
    """Call Bedrock converse API with retry and backoff."""
    user_prompt = build_user_prompt(kb_context, claims_batch)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": user_prompt}]}],
                system=[{"text": SYSTEM_PROMPT}],
                inferenceConfig={"temperature": 0.0, "maxTokens": 4096},
            )
            body = response["output"]["message"]["content"][0]["text"]
            return json.loads(body)
        except (client.exceptions.ThrottlingException, client.exceptions.ServiceUnavailableException) as exc:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = INITIAL_BACKOFF * (2 ** attempt)
            print(f"Retrying after {exc.__class__.__name__} (wait {wait:.1f}s)...", file=sys.stderr)
            time.sleep(wait)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Model returned non-JSON response: {exc}") from exc

    return []  # unreachable but satisfies linters


def main():
    parser = argparse.ArgumentParser(description="Cross-model claim verification via Bedrock")
    parser.add_argument("--claims", required=True, help="Path to claims JSON file")
    parser.add_argument("--kb-context", required=True, help="Path to KB context JSON file")
    parser.add_argument("--output", required=True, help="Path to write verification scores")
    parser.add_argument("--model", default="openai.gpt-oss-120b", help="Bedrock model ID")
    parser.add_argument("--region", default="us-west-2", help="AWS region")
    parser.add_argument("--profile", default=None, help="AWS profile name")
    args = parser.parse_args()

    with open(args.claims) as f:
        claims = json.load(f)
    with open(args.kb_context) as f:
        kb_context = json.load(f)

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    client = session.client("bedrock-runtime")

    all_results = []
    for i in range(0, len(claims), BATCH_SIZE):
        batch = claims[i : i + BATCH_SIZE]
        print(f"Verifying batch {i // BATCH_SIZE + 1} ({len(batch)} claims)...", file=sys.stderr)
        results = call_bedrock(client, args.model, kb_context, batch)
        all_results.extend(results)

    with open(args.output, "w") as f:
        json.dump(all_results, f, indent=2)

    supported = sum(1 for r in all_results if r.get("verdict") == "SUPPORTED")
    contradicted = sum(1 for r in all_results if r.get("verdict") == "CONTRADICTED")
    unverifiable = sum(1 for r in all_results if r.get("verdict") == "UNVERIFIABLE")
    print(
        f"Verified {len(all_results)} claims: "
        f"{supported} supported, {contradicted} contradicted, {unverifiable} unverifiable",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
