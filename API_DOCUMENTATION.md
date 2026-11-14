# VERITAS API Documentation

VERITAS exposes a Flask REST API. All POST endpoints accept JSON.

Base URL when running locally: `http://127.0.0.1:5000`

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serves the web interface |
| GET | `/api/health` | Checks whether the Flask API is running |
| POST | `/api/analyze` | Runs the ML prediction and independently retrieves fact-check and news-coverage evidence |
| POST | `/api/predict` | Legacy ML-only prediction endpoint |
| POST | `/api/fact-check` | Searches published reviews using Google Fact Check Tools |
| POST | `/api/news-coverage` | Searches recent news coverage using GDELT DOC 2.0 |

## Request body

The POST endpoints accept a JSON object with these fields:

```json
{
  "title": "Example news headline",
  "article": "The full text of the news article goes here..."
}
```

Both fields must be strings. The title may be empty when article text is supplied. The application limits the title to 1,000 characters and article text to 50,000 characters.

### Article requirements for analysis and prediction

- A full article is required; headline-only analysis is disabled.
- Article text must contain at least 100 characters.
- Basic quality checks reject very short, highly repetitive, or obviously malformed text.
- The unified analysis endpoint uses the headline as the external search query when available; otherwise it uses the first 500 characters of the article.

## GET /api/health

Successful response:

```json
{
  "status": "success",
  "message": "Fake News Detection API is running."
}
```

## POST /api/analyze

This is the main VERITAS 2.0 endpoint. It runs three independent operations:

1. The local TF-IDF + Logistic Regression model predicts whether the text resembles the Fake or Real class learned from WELFake.
2. Google Fact Check Tools is queried for previously published fact-check reviews. Returned claims receive lexical-overlap relevance labels.
3. GDELT DOC 2.0 is queried for matching news articles from the recent three-month period.

Successful response structure:

```json
{
  "status": "success",
  "result": {
    "prediction": 1,
    "label": "Real",
    "confidence": 79.9,
    "probabilities": {
      "Fake": 20.1,
      "Real": 79.9
    }
  },
  "evidence": {
    "fact_checks": {
      "status": "success",
      "source": "Google Fact Check Tools",
      "result": {
        "query": "Example news headline",
        "total_results": 1,
        "claims": [],
        "excluded_claims": [],
        "relevance_summary": {
          "direct_matches": 0,
          "related_claims": 0,
          "excluded_claims": 0,
          "method": "lexical_overlap_heuristic"
        }
      },
      "message": null
    },
    "news_coverage": {
      "status": "success",
      "source": "GDELT DOC 2.0",
      "result": {
        "query": "Example news headline",
        "total_results": 0,
        "articles": [],
        "timespan": "3m"
      },
      "message": null
    }
  },
  "disclaimer": "..."
}
```

The values above illustrate the response shape; counts and predictions depend on the submitted input and live services.

Each external evidence object can independently have `status: "success"` or `status: "unavailable"`. An external-service failure does not cancel a successful ML prediction. The ML result is not calculated from, or combined with, external evidence.

Typical HTTP responses:
- `200`: analysis completed; one or both external evidence sources may be unavailable.
- `400`: invalid JSON, invalid field types, missing article, input limits, or article-quality validation failure.
- `500`: the ML prediction could not be completed.

## POST /api/predict

Legacy ML-only endpoint. It accepts the same `title` and `article` JSON fields and returns `status`, `result`, and a disclaimer. It does not call either external evidence service.

## POST /api/fact-check

Searches Google Fact Check Tools using the title, or the first 500 article characters if no title is provided. The response includes:
- `claims`: results labelled `direct_match` or `related`
- `excluded_claims`: results labelled `irrelevant`
- `relevance_summary`: counts and the method identifier

The relevance score is query-term coverage expressed as a percentage. It is not a probability, semantic similarity score, or truth rating. Third-party textual ratings remain the responsibility of their publishers.

Typical errors: `400` for invalid input, `502` when the external API is unavailable, and `500` for an unexpected server error.

## POST /api/news-coverage

Searches GDELT DOC 2.0 for up to 10 recent matching articles within a three-month timespan. Each article may include a title, URL, domain, publication timestamp, language, source country, and image.

The presence or volume of matching coverage does not establish that a claim is true. Typical errors: `400` for invalid input, `502` when GDELT is unavailable or rate-limited, and `500` for an unexpected server error.

## Configuration and privacy

Set `GOOGLE_FACT_CHECK_API_KEY` in a local `.env` file in the project root. Do not commit the key or include it in screenshots, logs, or documentation. The `.env` file should remain ignored by Git.

The ML prediction runs using the locally loaded model. The headline or article-derived search query is sent to Google Fact Check Tools and GDELT for their respective external searches. Review the privacy notice in the interface before submitting text.

## Important interpretation note

VERITAS is an educational text-analysis tool, not an authoritative fact-checking service. Model predictions, lexical relevance labels, third-party reviews, and news-coverage results are separate outputs and must not be treated as interchangeable evidence.
