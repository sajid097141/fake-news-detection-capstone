# VERITAS — AI-Powered News Analysis

![Python](https://img.shields.io/badge/Python-3.11-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.1-orange)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black)
![Project](https://img.shields.io/badge/CBSE-Class%20XII%20AI%20Capstone-6c63ff)

A machine-learning-based educational project that analyses English news articles and classifies their writing patterns as **Fake** or **Real**, based on examples in the WELFake dataset.

> **Important:** VERITAS is a text-pattern classifier, not a fact-checking service. Its output does not establish whether a news story or claim is true.

**Subject:** Artificial Intelligence (843) · **Project:** CBSE Class XII Capstone  
**Author:** Sajid Ekbal Choudhury  
**School:** PM SHRI Kendriya Vidyalaya 210 CoBRA CRPF Dalgaon, Assam  
**Academic year:** 2026–27

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Dataset](#dataset)
- [Model Performance](#model-performance)
- [Project Structure](#project-structure)
- [Setup and Run](#setup-and-run)
- [API Endpoints](#api-endpoints)
- [Limitations](#limitations)
- [Disclaimer](#disclaimer)

## Overview

VERITAS uses a trained scikit-learn pipeline to analyse the text of a news article. The text is converted into numerical features using **TF-IDF** and passed to a **Logistic Regression** classifier.

The project includes a Flask web application with a browser-based interface. Users provide a headline and the full article text; the application returns the model's predicted class and its class-probability estimates.

The model was trained on labelled examples from WELFake. It learns statistical associations in that dataset and does not independently verify claims, consult news sources, or check the credibility of publishers.

## Features

- Browser-based interface built with HTML, CSS and JavaScript.
- Flask backend serving the trained machine-learning model.
- Full-article input with headline and article text.
- Fake/Real prediction with class-probability estimates.
- Input validation, including checks for missing, excessively long and low-quality/repetitive article text.
- Health-check endpoint for checking whether the API is running.
- Model and dataset evaluation using accuracy, precision, recall, F1-score and a confusion matrix.
- Runs locally after the required Python packages and model file are available; prediction does not require a paid API or external AI service.

## How It Works

1. **Input:** The user enters a headline and the full article text.
2. **Validation:** The Flask application checks the request and validates the article input.
3. **Text preparation:** The headline and article body are joined into one text string, matching the format used during training.
4. **Feature extraction:** The fitted TF-IDF vectorizer transforms the text into numerical features.
5. **Classification:** Logistic Regression predicts the class.
6. **Output:** The application displays the predicted label and model probability estimates.

### Model pipeline

`News text → TF-IDF Vectorizer → Logistic Regression → Predicted class`

The saved model is a complete scikit-learn Pipeline, so the vectorizer and classifier are loaded together.

## Technology Stack

| Area | Technology |
|---|---|
| Programming language | Python 3.11.9 |
| Machine learning | scikit-learn |
| Text representation | TF-IDF (unigrams and bigrams) |
| Classifier | Logistic Regression |
| Model persistence | joblib |
| Data processing | pandas, NumPy, SciPy |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Visualisation | Matplotlib, Seaborn |

Exact dependency versions are listed in [requirements.txt](requirements.txt).

## Dataset

- **Dataset:** WELFake
- **Source:** [WELFake dataset — Zenodo](https://zenodo.org/records/4561253)
- **Original records:** 72,134
- **Records after cleaning:** 63,676
- **Training samples:** 50,940
- **Test samples:** 12,736
- **Split:** 80% training / 20% testing, stratified by label, with `random_state=42`

### Label convention

| Label | Meaning |
|---:|---|
| `0` | Fake |
| `1` | Real |

The model was trained using the article title and body joined into a single text input. The web application therefore requires the full article body; headline-only predictions are not supported.

## Model Performance

The selected Logistic Regression model was evaluated on a held-out test set of 12,736 WELFake records.

### Overall metrics

| Metric | Result |
|---|---:|
| Accuracy | **95.90%** |
| Macro F1-score | **95.87%** |
| Correct predictions | 12,214 |
| Incorrect predictions | 522 |

### Class-wise metrics

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Fake | 96.21% | 96.29% | **96.25%** |
| Real | 95.53% | 95.43% | **95.48%** |

### Model comparison

| Model | Accuracy | Macro F1-score |
|---|---:|---:|
| **Logistic Regression (selected)** | **95.90%** | **95.87%** |
| Multinomial Naive Bayes | 88.87% | 88.80% |

These are test-set results from WELFake. They should not be interpreted as the application's real-world fact-checking accuracy.

## Project Structure

```text
CAPSTONE/
├── clean_data.py
├── audit_data.py
├── inspect_data.py
├── train_model.py
├── compare_models.py
├── evaluate_model.py
├── model_visuals.py
├── inspect_saved_model.py
├── test_model.py
├── test_dataset_samples.py
├── model_results.txt
├── requirements.txt
├── results/
├── docs/
└── webapp/
    ├── app.py
    ├── predictor.py
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── app.js
```

The raw dataset, cleaned dataset and trained model may be kept locally and are not necessarily included in the Git repository. The trained model is expected at the project root as `fake_news_model.joblib`.

## Setup and Run

### 1. Clone the repository

```bash
git clone https://github.com/sajid097141/fake-news-detection-capstone.git
cd fake-news-detection-capstone
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Add the trained model

Place the trained `fake_news_model.joblib` file in the repository root, alongside the main Python scripts. The Flask predictor loads the model from this location.

If you need to recreate the model, obtain the WELFake dataset from the source above and follow the data-cleaning and training scripts in the project.

### 5. Start the web application

From the repository root:

```bash
cd webapp
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

Stop the local server with `Ctrl + C` in the terminal.

## API Endpoints

The Flask application exposes these endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Loads the web interface |
| GET | `/api/health` | Returns the API health status |
| POST | `/api/predict` | Validates article input and returns a prediction |

### Prediction request

Send JSON containing a headline and full article body:

```json
{
  "title": "Example news headline",
  "article": "The full text of the news article goes here..."
}
```

A successful response contains a `result` object with the predicted label, confidence estimate and class-probability estimates, along with a disclaimer. Invalid input returns an error message and an appropriate HTTP status code.

## Limitations

- **Not a fact-checker:** The model does not verify claims against reliable sources or external databases.
- **Dataset dependence:** Evaluation is based on a random held-out split from WELFake. Real-world performance may differ.
- **Potential source and style bias:** The model may learn writing patterns associated with sources represented in the dataset.
- **Label quality:** Errors or inconsistencies in the dataset labels can affect the model.
- **Language and domain:** The model was trained on English news text and may not work reliably on other languages or very different writing styles.
- **Full-article input:** The model was trained on title-plus-article text. Short headlines alone are outside the intended input format.
- **Probability is not certainty:** The displayed confidence is the model's estimate, not a guarantee that its prediction is correct.

## Disclaimer

VERITAS is an educational AI capstone project. Its predictions reflect patterns learned from the WELFake training dataset and **do not independently determine whether news is true or false**. Always verify important claims using multiple reliable and independent sources. Do not use this tool as the sole basis for judging a person, publisher, article or news organisation.
