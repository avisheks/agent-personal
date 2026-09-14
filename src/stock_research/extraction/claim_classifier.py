"""Claim classifier -- extract structured investment claims from Reddit posts.

Stage 1.5 in the research pipeline: information extraction, not analysis.

Extracts from each post:
- bull_bear: "bull" / "bear" / "neutral"
- narratives: list of narrative labels (e.g. "AI_demand", "margin_expansion")
- claims: list of specific factual claims
- evidence_type: "fact" / "speculation" / "anecdote"
- confidence: 0.0-1.0

Two modes:
1. **LLM-based** (when ``llm_fn`` is provided): Uses a structured prompt to
   extract rich claim data via an LLM.
2. **Keyword-based** (default fallback): Basic heuristic classification using
   keyword matching -- no LLM dependency.

Output conforms to the ``investor_claims`` DuckDB schema.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword-based classification (fallback when no LLM is available)
# ---------------------------------------------------------------------------

_BULL_KEYWORDS: List[str] = [
    "bullish", "buy", "long", "undervalued", "upside", "growth",
    "beat", "outperform", "strong", "accelerat", "rocket", "moon",
    "breakout", "catalyst", "opportunity", "upgrade", "raise",
    "expanding", "beats expectations", "revenue growth", "market share",
]

_BEAR_KEYWORDS: List[str] = [
    "bearish", "sell", "short", "overvalued", "downside", "decline",
    "miss", "underperform", "weak", "decelerat", "crash", "bubble",
    "breakdown", "headwind", "risk", "downgrade", "cut",
    "shrinking", "misses expectations", "revenue decline", "losing share",
]

_NARRATIVE_PATTERNS: Dict[str, List[str]] = {
    "AI_demand": ["ai ", "artificial intelligence", "machine learning", "gpu", "data center", "llm"],
    "margin_expansion": ["margin", "profitability", "cost cutting", "efficiency", "operating leverage"],
    "margin_compression": ["margin pressure", "cost increase", "input cost", "wage inflation"],
    "competitive_threat": ["competition", "competitor", "market share loss", "disruption", "threat"],
    "moat_strength": ["moat", "barrier", "switching cost", "network effect", "brand strength"],
    "macro_risk": ["recession", "interest rate", "inflation", "fed ", "macro", "economic slowdown"],
    "management_quality": ["ceo", "management", "leadership", "execution", "capital allocation"],
    "valuation_concern": ["expensive", "overvalued", "pe ratio", "valuation", "priced in"],
    "valuation_opportunity": ["cheap", "undervalued", "discount", "bargain", "value play"],
    "dividend_income": ["dividend", "yield", "payout", "income", "distribution"],
    "buyback": ["buyback", "repurchase", "share reduction", "return capital"],
    "debt_concern": ["debt", "leverage", "interest expense", "refinancing", "credit"],
    "growth_acceleration": ["accelerat", "inflection", "ramp", "hockey stick", "hyper growth"],
    "regulatory_risk": ["regulation", "antitrust", "compliance", "sec ", "lawsuit", "legal"],
    "insider_activity": ["insider", "buying", "selling", "insider purchase", "insider sale"],
}

_FACT_INDICATORS: List[str] = [
    "according to", "reported", "data shows", "earnings", "revenue was",
    "grew by", "declined by", "filing", "sec ", "10-k", "10-q",
    "announced", "confirmed", "guidance", "forecast",
]

_SPECULATION_INDICATORS: List[str] = [
    "i think", "i believe", "probably", "might", "could",
    "seems like", "my guess", "imo", "imho", "in my opinion",
    "speculate", "predict", "expect", "bet", "likely",
]

_ANECDOTE_INDICATORS: List[str] = [
    "i work at", "my friend", "i noticed", "personally",
    "in my experience", "i saw", "i heard", "anecdot",
    "talked to", "someone told me", "my neighbor",
]


def _keyword_score(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _keyword_classify_single(post: dict, ticker: str) -> dict:
    """Classify a single post using keyword matching (no LLM).

    Parameters
    ----------
    post : dict
        Post dict with at least ``title`` and/or ``body`` (or ``text``/``content``).
    ticker : str
        Ticker symbol to filter relevance.

    Returns
    -------
    dict
        Classification result matching investor_claims schema.
    """
    title = str(post.get("title", ""))
    body = str(post.get("body") or post.get("text") or post.get("content") or "")
    combined = f"{title} {body}"
    combined_lower = combined.lower()

    # Bull/bear classification
    bull_score = _keyword_score(combined, _BULL_KEYWORDS)
    bear_score = _keyword_score(combined, _BEAR_KEYWORDS)

    if bull_score > bear_score + 1:
        bull_bear = "bull"
    elif bear_score > bull_score + 1:
        bull_bear = "bear"
    else:
        bull_bear = "neutral"

    # Narrative detection
    narratives: List[str] = []
    for narrative, patterns in _NARRATIVE_PATTERNS.items():
        if any(p in combined_lower for p in patterns):
            narratives.append(narrative)

    # Evidence type
    fact_score = _keyword_score(combined, _FACT_INDICATORS)
    spec_score = _keyword_score(combined, _SPECULATION_INDICATORS)
    anec_score = _keyword_score(combined, _ANECDOTE_INDICATORS)

    if anec_score > fact_score and anec_score > spec_score:
        evidence_type = "anecdote"
    elif fact_score > spec_score:
        evidence_type = "fact"
    else:
        evidence_type = "speculation"

    # Confidence: based on keyword density and ticker mention
    total_signals = bull_score + bear_score + len(narratives)
    ticker_mentioned = ticker.lower() in combined_lower or f"${ticker.lower()}" in combined_lower

    if total_signals >= 5 and ticker_mentioned:
        confidence = 0.7
    elif total_signals >= 3:
        confidence = 0.5
    elif total_signals >= 1:
        confidence = 0.3
    else:
        confidence = 0.1

    # Claims: extract sentences that contain claim-like patterns
    claims: List[str] = []
    sentences = re.split(r'[.!?\n]+', combined)
    claim_patterns = _FACT_INDICATORS + ["will ", "going to ", "should "]
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10 or len(sentence) > 300:
            continue
        if any(p in sentence.lower() for p in claim_patterns):
            claims.append(sentence.strip())
        if len(claims) >= 5:
            break

    return {
        "post_id": post.get("id") or post.get("post_id", ""),
        "ticker": ticker,
        "date": post.get("date") or post.get("created_utc") or post.get("created", ""),
        "source": post.get("source") or post.get("subreddit", "reddit"),
        "bull_bear": bull_bear,
        "narratives": narratives,
        "claims": claims,
        "evidence_type": evidence_type,
        "confidence": confidence,
        "title": title[:200] if title else "",
        "classification_method": "keyword",
    }


# ---------------------------------------------------------------------------
# LLM-based classification
# ---------------------------------------------------------------------------

def _build_classification_prompt(post: dict, ticker: str) -> str:
    """Build an LLM prompt to extract structured claims from a Reddit post.

    Parameters
    ----------
    post : dict
        Post dict with ``title`` and ``body``/``text``/``content``.
    ticker : str
        Ticker symbol being researched.

    Returns
    -------
    str
        Prompt string for the LLM.
    """
    title = str(post.get("title", ""))
    body = str(post.get("body") or post.get("text") or post.get("content") or "")
    # Truncate very long posts to avoid token waste
    if len(body) > 3000:
        body = body[:3000] + "... [truncated]"

    return f"""Analyze this Reddit post about {ticker} and extract investment claims.

POST TITLE: {title}
POST BODY: {body}

Return a JSON object with exactly these fields:
{{
  "bull_bear": "bull" | "bear" | "neutral",
  "narratives": ["list", "of", "narrative_labels"],
  "claims": ["list of specific factual claims made in the post"],
  "evidence_type": "fact" | "speculation" | "anecdote",
  "confidence": 0.0-1.0
}}

Guidelines:
- bull_bear: Overall investment thesis direction. "bull" if the post argues for buying/holding, "bear" if it argues for selling/shorting, "neutral" if balanced or off-topic.
- narratives: Use snake_case labels like: AI_demand, margin_expansion, margin_compression, competitive_threat, moat_strength, macro_risk, management_quality, valuation_concern, valuation_opportunity, dividend_income, buyback, debt_concern, growth_acceleration, regulatory_risk, insider_activity. Add new labels if needed.
- claims: Extract specific, verifiable factual claims (e.g. "revenue grew 20% YoY", "management guided for $5B in 2025"). Max 5 claims.
- evidence_type: "fact" if the post cites data/filings/earnings, "speculation" if it's opinion/prediction, "anecdote" if personal experience.
- confidence: How confident you are in this classification (0.0-1.0). Higher if the post is clearly about {ticker} with explicit thesis.

Return ONLY the JSON object, no other text."""


def _parse_classification(response: str) -> dict:
    """Parse the LLM's JSON response into a classification dict.

    Handles common LLM output quirks: markdown code fences, trailing commas,
    extra text around the JSON.

    Parameters
    ----------
    response : str
        Raw LLM response string.

    Returns
    -------
    dict
        Parsed classification, or a fallback dict with error info.
    """
    # Strip markdown code fences
    text = response.strip()
    if text.startswith("```"):
        # Remove opening fence (possibly with language tag)
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()

    # Try to find JSON object in the response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    # Remove trailing commas before closing braces/brackets (common LLM mistake)
    text = re.sub(r',\s*([}\]])', r'\1', text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse LLM classification response: %s", e)
        return {
            "bull_bear": "neutral",
            "narratives": [],
            "claims": [],
            "evidence_type": "speculation",
            "confidence": 0.0,
            "parse_error": str(e),
        }

    # Validate and normalize fields
    result: Dict[str, Any] = {}
    result["bull_bear"] = parsed.get("bull_bear", "neutral")
    if result["bull_bear"] not in ("bull", "bear", "neutral"):
        result["bull_bear"] = "neutral"

    result["narratives"] = parsed.get("narratives", [])
    if not isinstance(result["narratives"], list):
        result["narratives"] = []

    result["claims"] = parsed.get("claims", [])
    if not isinstance(result["claims"], list):
        result["claims"] = []
    # Limit to 5 claims
    result["claims"] = result["claims"][:5]

    result["evidence_type"] = parsed.get("evidence_type", "speculation")
    if result["evidence_type"] not in ("fact", "speculation", "anecdote"):
        result["evidence_type"] = "speculation"

    conf = parsed.get("confidence", 0.5)
    try:
        result["confidence"] = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        result["confidence"] = 0.5

    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def classify_claims(
    posts: List[Dict],
    ticker: str,
    llm_fn: Optional[Callable[[str], str]] = None,
) -> List[Dict]:
    """Classify investment claims from a list of Reddit posts.

    Parameters
    ----------
    posts : list[dict]
        Posts to classify. Each dict should have at minimum ``title`` and
        ``body`` (or ``text``/``content``). Optional: ``id``, ``date``,
        ``source``, ``subreddit``.
    ticker : str
        Ticker symbol being researched.
    llm_fn : callable, optional
        A function that takes a prompt string and returns an LLM response
        string. If not provided, falls back to keyword-based classification.

    Returns
    -------
    list[dict]
        List of classification dicts matching the ``investor_claims`` DuckDB
        schema. Each dict has: ``post_id``, ``ticker``, ``date``, ``source``,
        ``bull_bear``, ``narratives``, ``claims``, ``evidence_type``,
        ``confidence``, ``title``, ``classification_method``.
    """
    if not posts:
        return []

    results: List[Dict] = []

    for post in posts:
        if llm_fn is not None:
            # LLM-based classification
            try:
                prompt = _build_classification_prompt(post, ticker)
                response = llm_fn(prompt)
                classification = _parse_classification(response)

                result = {
                    "post_id": post.get("id") or post.get("post_id", ""),
                    "ticker": ticker,
                    "date": post.get("date") or post.get("created_utc") or post.get("created", ""),
                    "source": post.get("source") or post.get("subreddit", "reddit"),
                    "bull_bear": classification["bull_bear"],
                    "narratives": classification["narratives"],
                    "claims": classification["claims"],
                    "evidence_type": classification["evidence_type"],
                    "confidence": classification["confidence"],
                    "title": str(post.get("title", ""))[:200],
                    "classification_method": "llm",
                }
                results.append(result)
            except Exception as e:
                logger.warning(
                    "LLM classification failed for post %s, falling back to keyword: %s",
                    post.get("id", "unknown"),
                    e,
                )
                # Fall back to keyword classification
                results.append(_keyword_classify_single(post, ticker))
        else:
            # Keyword-based classification (no LLM)
            results.append(_keyword_classify_single(post, ticker))

    return results
