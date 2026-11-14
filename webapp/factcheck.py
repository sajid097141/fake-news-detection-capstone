"""Google Fact Check Tools API client for VERITAS.

This module retrieves existing fact-check reviews and estimates how closely
each returned claim matches the submitted search query. It does not
independently determine whether a claim is true.
"""

import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
TIMEOUT_SECONDS = 15

# Common words that add little value when comparing short claims.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "for", "from", "had", "has", "have", "he", "her", "his", "i",
    "in", "is", "it", "its", "of", "on", "or", "our", "she", "that",
    "the", "their", "them", "they", "this", "to", "was", "we", "were",
    "will", "with", "you", "your",
}


class FactCheckAPIError(Exception):
    """Raised when the Fact Check Tools API cannot be queried."""


def _claim_tokens(text):
    """Normalize text into meaningful lowercase word tokens."""
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


def assess_claim_relevance(query, claim_text):
    """Classify lexical overlap; this is not semantic or factual verification."""
    query_tokens = _claim_tokens(query)
    claim_tokens = _claim_tokens(claim_text)

    if not query_tokens or not claim_tokens:
        return {
            "label": "irrelevant",
            "score": 0,
            "matched_terms": [],
        }

    matched_terms = sorted(query_tokens & claim_tokens)
    overlap = len(matched_terms)
    query_coverage = overlap / len(query_tokens)
    union_size = len(query_tokens | claim_tokens)
    jaccard = overlap / union_size if union_size else 0

    normalized_query = " ".join(sorted(query_tokens))
    normalized_claim = " ".join(sorted(claim_tokens))

    if normalized_query == normalized_claim:
        label = "direct_match"
    elif (
        (query_coverage >= 0.85 and overlap >= 2 and jaccard >= 0.45)
        or (query_coverage >= 0.85 and overlap >= 3 and jaccard >= 0.25)
    ):
        label = "direct_match"
    elif (
        (query_coverage >= 0.50 and overlap >= 2)
        or jaccard >= 0.20
    ):
        label = "related"
    else:
        label = "irrelevant"

    return {
        "label": label,
        # A lexical overlap indicator, not a probability or truth score.
        "score": round(query_coverage * 100),
        "matched_terms": matched_terms,
    }


def add_relevance_labels(query, claims):
    """Attach relevance labels to API claims and split useful/excluded results."""
    relevant_claims = []
    excluded_claims = []

    for claim in claims:
        annotated = dict(claim)
        relevance = assess_claim_relevance(query, claim.get("claim_text", ""))
        annotated["relevance"] = relevance

        if relevance["label"] in {"direct_match", "related"}:
            relevant_claims.append(annotated)
        else:
            excluded_claims.append(annotated)

    return {
        "claims": relevant_claims,
        "excluded_claims": excluded_claims,
        "relevance_summary": {
            "direct_matches": sum(
                item["relevance"]["label"] == "direct_match"
                for item in relevant_claims
            ),
            "related_claims": sum(
                item["relevance"]["label"] == "related"
                for item in relevant_claims
            ),
            "excluded_claims": len(excluded_claims),
            "method": "lexical_overlap_heuristic",
        },
    }


def search_fact_checks(query, page_size=5):
    """Search existing fact-check reviews for a claim or phrase."""
    query = (query or "").strip()
    if not query:
        raise ValueError("A search query is required.")

    if not API_KEY:
        raise FactCheckAPIError(
            "Google Fact Check API key is not configured on the server."
        )

    params = {
        "key": API_KEY,
        "query": query[:500],
        "pageSize": max(1, min(int(page_size), 10)),
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise FactCheckAPIError(
            "Could not reach the Google Fact Check API."
        ) from exc

    if response.status_code != 200:
        # Do not expose the request URL because it contains the API key.
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = ""
        raise FactCheckAPIError(
            f"Google Fact Check API returned HTTP {response.status_code}."
            + (f" {detail}" if detail else "")
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise FactCheckAPIError(
            "Google Fact Check API returned invalid JSON."
        ) from exc

    results = []
    for claim in payload.get("claims", []):
        reviews = []
        for review in claim.get("claimReview", []):
            publisher = review.get("publisher") or {}
            reviews.append({
                "publisher": publisher.get("name"),
                "title": review.get("title"),
                "textual_rating": review.get("textualRating"),
                "url": review.get("url"),
                "review_date": review.get("reviewDate"),
                "language_code": review.get("languageCode"),
            })

        results.append({
            "claim_text": claim.get("text"),
            "claimant": claim.get("claimant"),
            "claim_date": claim.get("claimDate"),
            "reviews": reviews,
        })

    return {
        "query": query,
        "total_results": len(results),
        "claims": results,
    }
