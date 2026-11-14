"""Unit tests for VERITAS external API client error handling."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "webapp"))

import factcheck  # noqa: E402
import gdelt  # noqa: E402


class ExternalClientTests(unittest.TestCase):
    @patch.object(gdelt.requests, "get")
    def test_gdelt_translates_rate_limit(self, mock_get):
        mock_get.return_value = Mock(status_code=429)
        with self.assertRaisesRegex(gdelt.GDELTAPIError, "rate limit"):
            gdelt.search_news_coverage("A sufficiently long test query")

    @patch.object(gdelt.requests, "get")
    def test_gdelt_rejects_non_json_response(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            headers={"Content-Type": "text/html"},
        )
        with self.assertRaisesRegex(gdelt.GDELTAPIError, "non-JSON"):
            gdelt.search_news_coverage("A sufficiently long test query")

    @patch.object(gdelt.requests, "get")
    def test_gdelt_returns_empty_article_list(self, mock_get):
        response = Mock(status_code=200, headers={"Content-Type": "application/json"})
        response.json.return_value = {}
        mock_get.return_value = response

        result = gdelt.search_news_coverage("A sufficiently long test query")
        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["articles"], [])

    def test_gdelt_rejects_empty_query_without_network(self):
        with self.assertRaises(ValueError):
            gdelt.search_news_coverage("")

    @patch.object(factcheck.requests, "get")
    def test_factcheck_translates_http_error_without_leaking_key(self, mock_get):
        response = Mock(status_code=403)
        response.json.return_value = {
            "error": {"message": "API key not authorized"}
        }
        mock_get.return_value = response

        with patch.object(factcheck, "API_KEY", "test-secret-key"):
            with self.assertRaises(factcheck.FactCheckAPIError) as caught:
                factcheck.search_fact_checks("A sufficiently long test query")

        self.assertNotIn("test-secret-key", str(caught.exception))
        self.assertIn("HTTP 403", str(caught.exception))

    @patch.object(factcheck.requests, "get")
    def test_factcheck_handles_invalid_json(self, mock_get):
        response = Mock(status_code=200)
        response.json.side_effect = ValueError("invalid json")
        mock_get.return_value = response

        with patch.object(factcheck, "API_KEY", "test-key"):
            with self.assertRaisesRegex(factcheck.FactCheckAPIError, "invalid JSON"):
                factcheck.search_fact_checks("A sufficiently long test query")

    def test_relevance_filter_handles_empty_claim(self):
        result = factcheck.assess_claim_relevance("The Earth is flat", "")
        self.assertEqual(result["label"], "irrelevant")
        self.assertEqual(result["score"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
