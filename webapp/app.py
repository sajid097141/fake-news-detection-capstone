
from flask import Flask, request, jsonify, render_template
from predictor import predict_news

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


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
