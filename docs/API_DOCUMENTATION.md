# API Documentation

## 1. Overview

VERITAS — AI-Powered News Analysis uses a Flask backend to serve its web interface and expose HTTP endpoints for checking service status and classifying submitted news text.

The API uses JSON for request and response data. The prediction is produced by a trained scikit-learn pipeline loaded by the backend when the application starts.

**Base URL (local development):** `http://127.0.0.1:5000`

> **Important:** VERITAS identifies whether submitted text resembles the Fake or Real patterns learned from its training dataset. It does not independently verify claims, investigate sources, or establish whether an article is factually true.

## 2. Available Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serves the VERITAS web interface. |
| GET | `/api/health` | Checks whether the API is running. |
| POST | `/api/predict` | Validates submitted text and returns a model prediction. |

## 3. Health Check

### Request

```http
GET /api/health
```

No request body is required.

### Successful response — `200 OK`

```json
{
  "status": "success",
  "message": "Fake News Detection API is running."
}
```

This endpoint confirms that the Flask application is responding. It does not perform a model accuracy test.

## 4. News Prediction

### Request

```http
POST /api/predict
Content-Type: application/json
```

### Request body

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | String | No | News headline. Defaults to an empty string if omitted. |
| `article` | String | Yes | Full article text to be analysed. |

Example:

```json
{
  "title": "Example news headline",
  "article": "The full text of the news article goes here. Provide the complete article text for analysis, with enough detail to meet the input validation requirements."
}
```

The model was trained using the headline and article text together. The application therefore combines the supplied title and article before sending the text to the trained model. Although the title is optional in the API, the article is mandatory. Headline-only predictions are disabled.

### Input validation

The endpoint applies the following checks before prediction:

- The request body must contain valid JSON representing an object.
- The `title` and `article` fields must be strings.
- The title cannot exceed 1,000 characters.
- The article cannot exceed 50,000 characters.
- The article must not be empty.
- The article must contain at least 100 characters and at least 20 words.
- The application rejects certain low-quality inputs, including unusually repeated characters, excessively repeated lines, and highly repetitive wording.

If validation fails, the API returns an error message with HTTP status `400 Bad Request`.

### Successful response — `200 OK`

```json
{
  "status": "success",
  "result": {
    "prediction": 1,
    "label": "Real",
    "confidence": 95.48,
    "probabilities": {
      "Fake": 4.52,
      "Real": 95.48
    }
  },
  "disclaimer": "This prediction reflects patterns learned from the training dataset. It does not verify facts."
}
```

The values above are an illustrative response format, not the result of a specific live prediction.

### Response fields

| Field | Type | Description |
|---|---|---|
| `status` | String | Indicates successful processing. |
| `result.prediction` | Integer | Predicted class: `0` for Fake or `1` for Real. |
| `result.label` | String | Human-readable predicted class: `Fake` or `Real`. |
| `result.confidence` | Number | Model probability for the predicted class, expressed as a percentage. |
| `result.probabilities.Fake` | Number | Model probability assigned to the Fake class, as a percentage. |
| `result.probabilities.Real` | Number | Model probability assigned to the Real class, as a percentage. |
| `disclaimer` | String | Explains that the output is based on learned dataset patterns and is not fact verification. |

Probabilities are model outputs, not guarantees or measures of factual certainty.

## 5. Error Responses

The API returns JSON error messages when a request cannot be processed.

### Common client errors — `400 Bad Request`

Examples include:

**Invalid JSON or non-object request body**
```json
{
  "error": "Invalid request. Please send JSON data."
}
```

**Missing article**
```json
{
  "error": "Please provide the full article. Headline-only predictions are disabled."
}
```

**Article shorter than the minimum character limit**
```json
{
  "error": "Please provide at least 100 characters of article text."
}
```

Other validation errors return an `error` field with a message explaining the issue. These include incorrect field types, input length limits, and article-quality checks.

### Internal server error — `500 Internal Server Error`

If an unexpected error occurs during processing, the API returns:

```json
{
  "error": "An internal error occurred while processing the text."
}
```

The detailed exception is recorded in the Flask application log; it is not exposed in the API response.

## 6. Prediction Workflow

1. The client submits a POST request containing the title and full article.
2. Flask parses the JSON request.
3. The backend validates the input fields, lengths, and article quality.
4. The `predict_news()` function combines the title and article.
5. The pre-trained scikit-learn pipeline generates a class prediction and class probabilities.
6. The backend maps the class IDs to the labels `Fake` and `Real`.
7. Flask returns the prediction, confidence, probabilities, and disclaimer as JSON.

## 7. Running the API Locally

From the project's `webapp` directory, run:

```powershell
python app.py
```

The development server is configured to run at:

```text
http://127.0.0.1:5000
```

Open that address in a browser to access the web interface. The API endpoints can also be tested using an HTTP client such as Postman or the browser's developer tools.

The trained model file, `fake_news_model.joblib`, is expected in the project root, one directory above `webapp`.

## 8. Technology and Implementation Notes

- **Backend framework:** Flask
- **Request/response format:** JSON for API endpoints
- **Machine learning:** scikit-learn pipeline
- **Model loading:** joblib
- **Prediction module:** `webapp/predictor.py`
- **Backend routes:** `webapp/app.py`

VERITAS uses Flask; it does not use FastAPI.

## 9. Limitations and Responsible Use

- The API performs text classification based on patterns learned from the WELFake dataset.
- It does not connect to external fact-checking services or verify article sources.
- A high confidence score does not prove that an article is true or false.
- Dataset performance may not represent performance on current, unseen, or real-world news.
- Results should be treated as an educational machine-learning prediction and not as the sole basis for sharing, trusting, or rejecting a news report.
