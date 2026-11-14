"""GDELT DOC 2.0 client for VERITAS news-coverage discovery.

GDELT returns news articles matching a query. Coverage volume or the presence
of an article is not proof that a claim is true.
"""

import requests

API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
TIMEOUT_SECONDS = 20


class GDELTAPIError(Exception):
    """Raised when the GDELT DOC API cannot be queried."""


def search_news_coverage(query, max_records=10, timespan="3m"):
    """Search recent news articles matching a headline or claim."""
    query = (query or "").strip()
    if not query:
        raise ValueError("A search query is required.")

    params = {
        "query": query[:500],
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max(1, min(int(max_records), 50)),
        "timespan": timespan,
        "sort": "DateDesc",
    }

    headers = {
        "User-Agent": "VERITAS/2.0 news coverage research"
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise GDELTAPIError(
            "Could not reach the GDELT news search service."
        ) from exc

    if response.status_code == 429:
        raise GDELTAPIError(
            "GDELT rate limit reached. Please wait a few seconds before retrying."
        )

    if response.status_code != 200:
        raise GDELTAPIError(
            f"GDELT returned HTTP {response.status_code}."
        )

    content_type = response.headers.get("Content-Type", "").lower()
    if "json" not in content_type:
        raise GDELTAPIError(
            "GDELT returned a non-JSON response. The query may be invalid or the service may be busy."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise GDELTAPIError(
            "GDELT returned invalid JSON."
        ) from exc

    articles = []
    for item in payload.get("articles", []):
        articles.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "domain": item.get("domain"),
            "published_at": item.get("seendate"),
            "language": item.get("language"),
            "source_country": item.get("sourcecountry"),
            "image": item.get("socialimage"),
        })

    return {
        "query": query,
        "total_results": len(articles),
        "articles": articles,
        "timespan": timespan,
    }
