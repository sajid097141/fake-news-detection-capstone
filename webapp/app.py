from flask import Flask, request, jsonify, render_template
from predictor import predict_news
from factcheck import (
    search_fact_checks,
    add_relevance_labels,
    FactCheckAPIError,
)
from gdelt import search_news_coverage, GDELTAPIError

import re
from collections import Counter

app = Flask(__name__)


def check_article_quality(article):
    """Reject obviously repetitive or low-quality article input."""

    words = re.findall(r"\b[\w']+\b", article.lower())

    if len(words) < 20:
        return "Please provide a more detailed article with at least 20 words."

    # Detect repeated characters
    if re.search(r"(.)\1{7,}", article):
        return "Your article contains unusually repeated characters."

    # Detect repeated lines
    lines = [
        line.strip().lower()
        for line in article.splitlines()
        if len(line.strip()) >= 30
    ]

    line_counts = Counter(lines)

    if any(count >= 3 for count in line_counts.values()):
        return "Your article contains excessively repeated lines."

    # Detect repetitive vocabulary
    unique_ratio = len(set(words)) / len(words)

    if len(words) >= 30 and unique_ratio < 0.30:
        return "Your article contains highly repetitive wording."

    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Fake News Detection API is running."
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request. Please send JSON data."
            }), 400

        title = data.get("title", "")
        article = data.get("article", "")

        if not isinstance(title, str) or not isinstance(article, str):
            return jsonify({
                "error": "Headline and article must be text."
            }), 400

        title = title.strip()
        article = article.strip()

        # Maximum input limits
        if len(title) > 1000:
            return jsonify({
                "error": "Headline cannot exceed 1,000 characters."
            }), 400

        if len(article) > 50000:
            return jsonify({
                "error": "Article cannot exceed 50,000 characters."
            }), 400

        # Require an article
        if not article:
            return jsonify({
                "error": "Please provide the full article. Headline-only predictions are disabled."
            }), 400

        # Minimum article length
        if len(article) < 100:
            return jsonify({
                "error": "Please provide at least 100 characters of article text."
            }), 400

        # Article quality checks
        quality_error = check_article_quality(article)

        if quality_error:
            return jsonify({
                "error": quality_error
            }), 400

        # Run the trained model
        result = predict_news(title, article)

        return jsonify({
            "status": "success",
            "result": result,
            "disclaimer": (
                "This prediction reflects patterns learned from the "
                "training dataset. It does not verify facts."
            )
        })

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Prediction failed")

        return jsonify({
            "error": "An internal error occurred while processing the text."
        }), 500


@app.route("/api/fact-check", methods=["POST"])
def fact_check():
    """Retrieve and classify published fact-check reviews by claim relevance."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request. Please send JSON data."
        }), 400

    title = data.get("title", "")
    article = data.get("article", "")

    if not isinstance(title, str) or not isinstance(article, str):
        return jsonify({
            "error": "Headline and article must be text."
        }), 400

    title = title.strip()
    article = article.strip()

    if len(title) > 1000 or len(article) > 50000:
        return jsonify({
            "error": "Input exceeds the allowed character limit."
        }), 400

    # Prefer the headline because it is usually a more focused search query.
    # If no headline is supplied, use the beginning of the article.
    query = title or article[:500]

    if len(query) < 10:
        return jsonify({
            "error": "Please provide a longer headline or article for fact-check search."
        }), 400

    try:
        raw_result = search_fact_checks(query, page_size=5)
        relevance_result = add_relevance_labels(
            query,
            raw_result["claims"],
        )

        result = {
            "query": raw_result["query"],
            "total_results": raw_result["total_results"],
            **relevance_result,
        }

        return jsonify({
            "status": "success",
            "source": "Google Fact Check Tools",
            "result": result,
            "disclaimer": (
                "Relevance labels are based on lexical overlap, not semantic "
                "verification. Related claims may discuss a different assertion. "
                "Third-party ratings are not independent conclusions by VERITAS."
            )
        })

    except FactCheckAPIError as error:
        app.logger.warning("Fact-check lookup failed: %s", error)
        return jsonify({
            "error": str(error)
        }), 502

    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid fact-check search input."
        }), 400

    except Exception:
        app.logger.exception("Fact-check lookup failed")
        return jsonify({
            "error": "An internal error occurred during live fact-check search."
        }), 500


@app.route("/api/news-coverage", methods=["POST"])
def news_coverage():
    """Find recent news coverage matching a headline or claim."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request. Please send JSON data."}), 400

    title = data.get("title", "")
    article = data.get("article", "")

    if not isinstance(title, str) or not isinstance(article, str):
        return jsonify({"error": "Headline and article must be text."}), 400

    title = title.strip()
    article = article.strip()

    if len(title) > 1000 or len(article) > 50000:
        return jsonify({"error": "Input exceeds the allowed character limit."}), 400

    query = title or article[:500]
    if len(query) < 10:
        return jsonify({"error": "Please provide a longer headline or article for news search."}), 400

    try:
        result = search_news_coverage(query, max_records=10, timespan="3m")
        return jsonify({
            "status": "success",
            "source": "GDELT DOC 2.0",
            "result": result,
            "disclaimer": (
                "These are news articles matching your search query. "
                "Their presence, number, or publication does not establish "
                "whether the submitted claim is true."
            ),
        })
    except GDELTAPIError as error:
        app.logger.warning("GDELT news search failed: %s", error)
        return jsonify({"error": str(error)}), 502
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid news search input."}), 400
    except Exception:
        app.logger.exception("GDELT news search failed")
        return jsonify({"error": "An internal error occurred during news coverage search."}), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
