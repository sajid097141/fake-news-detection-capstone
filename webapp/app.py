
from flask import Flask, request, jsonify, render_template
from predictor import predict_news

app = Flask(__name__)


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
                "error": "Title and article must be text."
            }), 400

        if len(title) > 1000 or len(article) > 50000:
            return jsonify({
                "error": "Input is too long."
            }), 400

        if not title.strip() and not article.strip():
            return jsonify({
                "error": "Please enter a headline or article."
            }), 400

        result = predict_news(title, article)

        return jsonify({
            "status": "success",
            "result": result,
            "disclaimer": (
                "This prediction reflects patterns learned from "
                "the training dataset. It does not verify facts."
            )
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "An internal error occurred while processing the text."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

