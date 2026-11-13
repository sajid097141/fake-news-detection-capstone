# Testing and Validation

## 1. Purpose

This document describes the testing performed on the VERITAS machine-learning workflow and Flask web application. Testing checks that the saved model can be loaded, valid text can be processed, the API returns the expected response structure, and invalid input is rejected.

A successful software test does not establish that a prediction is factually correct. VERITAS classifies text according to patterns learned from the WELFake dataset; it does not independently verify news claims or sources.

## 2. Testing Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.11.9 |
| Backend | Flask |
| Machine-learning library | scikit-learn |
| Model persistence | joblib |
| Local server | http://127.0.0.1:5000 |
| API request format | JSON |

Install project dependencies from the repository root:

    python -m pip install -r requirements.txt

The trained model file, fake_news_model.joblib, must be present in the project root before importing the prediction module or starting the web application.

## 3. Testing Levels

### 3.1 Model and pipeline checks

The project includes scripts that inspect the dataset, inspect the saved model, evaluate the classifier and run predictions.

| Script | Purpose |
|---|---|
| inspect_data.py | Checks dataset shape, columns, missing values, class distribution and sample records. |
| audit_data.py | Checks missing values, duplicate rows, empty combined text and duplicate texts with conflicting labels. |
| inspect_saved_model.py | Loads the saved pipeline and reports its steps, classes, TF-IDF vocabulary size and classifier details. |
| evaluate_model.py | Recreates the stratified 80:20 split and reports classification metrics; saves a confusion-matrix image. |
| test_model.py | Provides an interactive command-line prediction test. |
| test_dataset_samples.py | Samples five records from each class and compares model predictions with their dataset labels. |

Run these scripts from the project root, after preparing the required data and model files. For example:

    python inspect_saved_model.py
    python evaluate_model.py
    python test_model.py
    python test_dataset_samples.py

**Interpretation note:** test_dataset_samples.py selects records from the cleaned dataset used in the training workflow. Its output is a basic pipeline sanity check, not an independent generalisation test. The held-out test-set evaluation from evaluate_model.py is the relevant source for the reported test metrics.

### 3.2 Flask API checks

The Flask application exposes a health endpoint and a prediction endpoint.

Start the application from the webapp directory:

    cd webapp
    python app.py

The development server should report that it is running at http://127.0.0.1:5000.

Open a second PowerShell terminal for the API requests below.

#### Health check

    Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health" -Method GET

Expected response:

    {
      "status": "success",
      "message": "Fake News Detection API is running."
    }

#### Valid prediction request

    $body = @{
        title = "India's Chandrayaan-3 Successfully Lands Near the Moon's South Pole"
        article = "India's Chandrayaan-3 mission successfully completed a historic soft landing on the Moon on 23 August 2023. The Vikram lander touched down in the Moon's southern high-latitude region, making India the fourth country to achieve a controlled soft landing on the lunar surface. Following the landing, the Pragyan rover rolled down from the lander and began exploring the surrounding area. The mission carried scientific instruments designed to study the lunar surface."
    } | ConvertTo-Json

    Invoke-RestMethod `
        -Uri "http://127.0.0.1:5000/api/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body

A successful response should contain:

- status: success
- A result object containing prediction, label, confidence and probabilities
- A disclaimer explaining that the prediction does not verify facts

The exact predicted label and percentages depend on the saved model. They should not be hard-coded into a test expectation.

### 3.3 Browser interface checks

Open http://127.0.0.1:5000/ in a browser and check the following:

1. The VERITAS home page loads.
2. The headline and article fields accept text.
3. The article character and word counters update while typing.
4. Submitting a valid full article displays a prediction.
5. The result panel displays the label, confidence and Fake/Real probability values.
6. The clear action resets the form and its displayed state.
7. Validation or network errors are presented to the user without displaying a false successful prediction.

## 4. Input Validation Test Cases

The Flask backend validates the JSON request before calling the model.

| Test ID | Input or condition | Expected behaviour |
|---|---|---|
| VAL-01 | Request body is not valid JSON or is not a JSON object | HTTP 400 with an error message. |
| VAL-02 | Headline or article value is not a string | HTTP 400 with a text-type validation message. |
| VAL-03 | Headline exceeds 1,000 characters | HTTP 400; request is rejected. |
| VAL-04 | Article exceeds 50,000 characters | HTTP 400; request is rejected. |
| VAL-05 | Article is empty | HTTP 400; full article is required. |
| VAL-06 | Article contains fewer than 100 characters | HTTP 400; minimum article length message. |
| VAL-07 | Article contains fewer than 20 words | HTTP 400; detailed article message from the quality check. |
| VAL-08 | Article contains a character repeated at least eight consecutive times | HTTP 400; repeated-character warning. |
| VAL-09 | A line of at least 30 characters is repeated three or more times | HTTP 400; repeated-lines warning. |
| VAL-10 | Article has at least 30 words but a unique-word ratio below 0.30 | HTTP 400; repetitive-wording warning. |
| VAL-11 | Valid headline and full article are supplied | Request proceeds to model inference. |

The quality checks are simple input filters. They do not establish whether an article is genuine, well-written or factually accurate.

## 5. Observed Manual Test Results

The following checks were performed during local development:

| Test | Observed result |
|---|---|
| Flask application startup | Passed; local development server started on port 5000. |
| Health endpoint | Passed; returned a JSON success message. |
| Valid prediction API request | Passed; returned a prediction result and disclaimer. |
| Repetitive article rejection | Passed; the API returned the expected repetitive-wording validation error. |
| Valid article through browser interface | Passed; prediction label, confidence and class probabilities were displayed. |
| Headline-only request | Rejected by the backend, as intended. |

These are manual development checks, not the results of a formal automated test suite. The remaining validation cases in Section 4 are documented test scenarios and should not be interpreted as individually executed unless separately tested.

## 6. Model Evaluation Results

The Logistic Regression model was evaluated on a stratified held-out test split containing 12,736 WELFake records.

| Metric | Result |
|---|---:|
| Accuracy | 95.90% |
| Macro F1-score | 95.87% |
| Correct predictions | 12,214 |
| Incorrect predictions | 522 |

Class-wise results:

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Fake | 96.21% | 96.29% | 96.25% |
| Real | 95.53% | 95.43% | 95.48% |

These are dataset evaluation results, not API pass rates or guaranteed real-world accuracy. Refer to MODEL_DOCUMENTATION.md for the model configuration and PROJECT_OVERVIEW.md for the project context.

## 7. Error Handling

The API uses the following response behaviour:

| Situation | HTTP status |
|---|---:|
| Successful prediction | 200 |
| Invalid JSON or input validation failure | 400 |
| Unexpected server-side prediction error | 500 |

For an unexpected exception, the backend logs the exception and returns a generic error message. Internal exception details are not returned to the browser.

The frontend also handles unsuccessful HTTP responses, network failures and requests that exceed its configured timeout.

## 8. Known Limitations

- The model learns from the WELFake dataset and may not generalise to all publishers, topics, writing styles or future news.
- A high confidence score is not proof that an article is true or false.
- The application does not browse the internet, consult external fact-checking services or verify sources.
- The current API requires a full article; headline-only analysis is disabled.
- The manual API and browser checks do not replace a comprehensive automated test suite.
- The local Flask development server is not intended for public production deployment.

## 9. Conclusion

Testing confirmed that the saved model can be loaded and used through the Flask application, the health endpoint responds, valid full-article requests return model predictions, and repetitive or incomplete input can be rejected. The model's held-out WELFake evaluation provides a separate measure of classification performance on the dataset.

Further automated testing and evaluation on independent, unseen news sources would be needed before making stronger claims about reliability outside the training dataset.
