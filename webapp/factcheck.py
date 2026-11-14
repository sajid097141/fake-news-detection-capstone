"""Google Fact Check Tools API client for VERITAS.

This module retrieves existing fact-check reviews; it does not independently
determine whether a claim is true.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
TIMEOUT_SECONDS = 15


class FactCheckAPIError(Exception):
    """Raised when the Fact Check Tools API cannot be queried."""


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
