"""Automated API edge-case tests for VERITAS.

Run from the repository root with:
    python -m unittest discover -s tests -v

External services are mocked so the suite is repeatable and does not consume
API quota or depend on GDELT availability.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEBAPP_DIR = PROJECT_ROOT / "webapp"
sys.path.insert(0, str(WEBAPP_DIR))

from webapp import app as veritas_app  # noqa: E402


VALID_ARTICLE = (
    "Officials announced a new public transport programme on Tuesday. "
    "The project will improve regional connections, add electric buses, "
    "upgrade stations, and publish quarterly progress reports for residents. "
    "Independent reviewers will assess costs, construction milestones, "
    "passenger demand, and environmental effects before later phases begin."
)

MODEL_RESULT = {
    "prediction": 1,
    "label": "Real",
    "confidence": 79.9,
    "probabilities": {"Fake": 20.1, "Real": 79.9},
}

FACT_CHECK_RESULT = {
    "query": "Test headline about transport",
    "total_results": 1,
    "claims": [{
        "claim_text": "Test headline about transport",
        "claimant": None,
        "claim_date": None,
        "reviews": [{
            "publisher": "Example Fact Checker",
            "title": "Review of transport claim",
            "textual_rating": "Unsupported",
            "url": "https://example.org/fact-check",
            "review_date": "2026-01-01",
            "language_code": "en",
        }],
    }],
}

GDELT_RESULT = {
    "query": "Test headline about transport",
    "total_results": 1,
    "articles": [{
        "title": "Transport programme announced",
        "url": "https://example.org/news",
        "domain": "example.org",
        "published_at": "20261114090000",
        "language": "English",
        "source_country": "United States",
        "image": None,
    }],
    "timespan": "3m",
}


class VeritasAPITests(unittest.TestCase):
    def setUp(self):
        veritas_app.app.config.update(TESTING=True)
        self.client = veritas_app.app.test_client()
        self.payload = {
            "title": "Test headline about transport",
            "article": VALID_ARTICLE,
        }

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")

    def test_analyze_rejects_non_json(self):
        response = self.client.post(
            "/api/analyze",
            data="not-json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_analyze_rejects_non_object_json(self):
        response = self.client.post("/api/analyze", json=["not", "an", "object"])
        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_wrong_field_types(self):
        response = self.client.post(
            "/api/analyze",
            json={"title": 123, "article": VALID_ARTICLE},
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_missing_article(self):
        response = self.client.post(
            "/api/analyze",
            json={"title": "A sufficiently long headline"},
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_short_article(self):
        response = self.client.post(
            "/api/analyze",
            json={"title": "A sufficiently long headline", "article": "Too short."},
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_oversized_headline(self):
        response = self.client.post(
            "/api/analyze",
            json={"title": "x" * 1001, "article": VALID_ARTICLE},
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_oversized_article(self):
        response = self.client.post(
            "/api/analyze",
            json={"title": "A sufficiently long headline", "article": "x" * 50001},
        )
        self.assertEqual(response.status_code, 400)

    @patch.object(veritas_app, "search_news_coverage", return_value=GDELT_RESULT)
    @patch.object(veritas_app, "search_fact_checks", return_value=FACT_CHECK_RESULT)
    @patch.object(veritas_app, "predict_news", return_value=MODEL_RESULT)
    def test_analyze_returns_all_three_streams(self, mock_predict, mock_facts, mock_news):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["result"]["label"], "Real")
        self.assertEqual(body["evidence"]["fact_checks"]["status"], "success")
        self.assertEqual(body["evidence"]["news_coverage"]["status"], "success")
        mock_predict.assert_called_once()
        mock_facts.assert_called_once()
        mock_news.assert_called_once()

    @patch.object(
        veritas_app,
        "search_news_coverage",
        side_effect=veritas_app.GDELTAPIError("GDELT rate limit reached."),
    )
    @patch.object(veritas_app, "search_fact_checks", return_value=FACT_CHECK_RESULT)
    @patch.object(veritas_app, "predict_news", return_value=MODEL_RESULT)
    def test_gdelt_failure_does_not_break_analysis(self, mock_predict, mock_facts, mock_news):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"]["label"], "Real")
        self.assertEqual(body["evidence"]["fact_checks"]["status"], "success")
        self.assertEqual(body["evidence"]["news_coverage"]["status"], "unavailable")
        self.assertIn("rate limit", body["evidence"]["news_coverage"]["message"].lower())

    @patch.object(veritas_app, "search_news_coverage", return_value=GDELT_RESULT)
    @patch.object(
        veritas_app,
        "search_fact_checks",
        side_effect=veritas_app.FactCheckAPIError("Google API unavailable."),
    )
    @patch.object(veritas_app, "predict_news", return_value=MODEL_RESULT)
    def test_factcheck_failure_does_not_break_analysis(self, mock_predict, mock_facts, mock_news):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"]["label"], "Real")
        self.assertEqual(body["evidence"]["fact_checks"]["status"], "unavailable")
        self.assertEqual(body["evidence"]["news_coverage"]["status"], "success")

    @patch.object(
        veritas_app,
        "search_news_coverage",
        side_effect=veritas_app.GDELTAPIError("GDELT rate limit reached."),
    )
    @patch.object(
        veritas_app,
        "search_fact_checks",
        side_effect=veritas_app.FactCheckAPIError("Google API unavailable."),
    )
    @patch.object(veritas_app, "predict_news", return_value=MODEL_RESULT)
    def test_both_external_services_down_still_returns_model(self, mock_predict, mock_facts, mock_news):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"]["label"], "Real")
        self.assertEqual(body["evidence"]["fact_checks"]["status"], "unavailable")
        self.assertEqual(body["evidence"]["news_coverage"]["status"], "unavailable")

    @patch.object(veritas_app, "search_news_coverage", return_value=GDELT_RESULT)
    @patch.object(veritas_app, "search_fact_checks", return_value=FACT_CHECK_RESULT)
    @patch.object(veritas_app, "predict_news", side_effect=RuntimeError("model failure"))
    def test_model_failure_returns_server_error(self, mock_predict, mock_facts, mock_news):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())
        mock_facts.assert_not_called()
        mock_news.assert_not_called()

    @patch.object(veritas_app, "predict_news", return_value=MODEL_RESULT)
    def test_legacy_predict_endpoint_still_works(self, mock_predict):
        response = self.client.post("/api/predict", json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"]["label"], "Real")

    def test_legacy_predict_rejects_invalid_payload(self):
        response = self.client.post("/api/predict", json={"title": "Headline"})
        self.assertEqual(response.status_code, 400)

    def test_factcheck_endpoint_rejects_empty_query(self):
        response = self.client.post("/api/fact-check", json={"title": "", "article": ""})
        self.assertEqual(response.status_code, 400)

    def test_news_endpoint_rejects_empty_query(self):
        response = self.client.post("/api/news-coverage", json={"title": "", "article": ""})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
