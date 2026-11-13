# Project Overview

## 1. Project Identity

| Detail | Information |
|---|---|
| Project name | **VERITAS — AI-Powered News Analysis** |
| Project type | Machine-learning-based news text classification system |
| Academic programme | CBSE Class XII Artificial Intelligence (843) Capstone |
| Academic year | 2026–27 |
| Student | Sajid Ekbal Choudhury |
| School | PM SHRI Kendriya Vidyalaya 210 CoBRA CRPF Dalgaon, Assam |
| Primary language | Python |
| Web framework | Flask |

## 2. Introduction

The internet allows news and information to circulate rapidly. Alongside useful reporting, readers may encounter misleading or fabricated content. Distinguishing reliable information from misleading material can be difficult, particularly when articles are shared without context.

**VERITAS** is an educational machine-learning project that demonstrates how natural language processing and supervised text classification can be applied to news articles. It analyses the text of an article and predicts whether its writing patterns resemble the Fake or Real examples in the WELFake dataset.

The project combines a trained machine-learning model with a Flask-based web application, allowing a user to submit a headline and the full article text through a browser interface.

**VERITAS is not a fact-checking service.** It does not verify statements against evidence, consult external news sources, or establish the factual truth of an article. Its output is a prediction based on patterns learned from its training dataset.

## 3. Problem Statement

News content is widely shared online, and readers may find it difficult to assess unfamiliar articles. Manually reviewing large amounts of text can take time, while the language and presentation of an article may influence how readers perceive it.

This project explores whether a supervised machine-learning model can learn textual patterns from a labelled news dataset and use those patterns to classify an article into one of two dataset-defined categories: Fake or Real.

The project also provides a simple browser-based interface so that the model can be demonstrated without requiring users to interact directly with Python scripts.

## 4. Aim

To design and develop an educational AI-based news text classification system that uses Natural Language Processing and machine learning to analyse a full news article and predict whether its textual patterns resemble the Fake or Real class in the WELFake dataset.

## 5. Objectives

The main objectives are to:

1. Study and use a labelled news dataset suitable for binary text classification.
2. Audit and clean the dataset by handling missing values, empty records and duplicate article text.
3. Combine each news headline and article body into a single text input.
4. Convert textual data into numerical features using TF-IDF.
5. Train and evaluate Logistic Regression as the primary classification algorithm.
6. Compare Logistic Regression with Multinomial Naive Bayes using the same data split and feature-extraction configuration.
7. Evaluate the selected model using accuracy, precision, recall, F1-score and a confusion matrix.
8. Save the fitted machine-learning pipeline so it can be reused without retraining for every prediction.
9. Develop a Flask web application that accepts article text and displays the model's prediction and probability estimates.
10. Communicate the model's limitations and encourage independent verification of important claims.

## 6. Proposed Solution

VERITAS uses a supervised text-classification pipeline.

The user enters a headline and the full text of a news article. The Flask backend validates the input and combines the headline with the article body. The saved TF-IDF and Logistic Regression pipeline then processes the text and returns a predicted class and class-probability estimates.

### High-level workflow

```text
User enters headline and full article
                |
                v
       Flask input validation
                |
                v
      Combine title and article
                |
                v
       Fitted TF-IDF vectorizer
                |
                v
       Logistic Regression
                |
                v
       Fake / Real prediction
                |
                v
    Display result and probabilities
```

The application requires the full article body. Headline-only predictions are disabled because the model was trained on combined title-and-article text.

## 7. Dataset

The project uses the **WELFake dataset**.

- Original records: **72,134**
- Records after cleaning: **63,676**
- Training records: **50,940**
- Testing records: **12,736**
- Train-test split: **80:20**
- Split method: stratified, with `random_state=42`

The dataset uses the following label convention:

| Label | Category |
|---:|---|
| 0 | Fake |
| 1 | Real |

Dataset source: [WELFake dataset on Zenodo](https://zenodo.org/records/4561253).

## 8. Machine-Learning Approach

### Text feature extraction

The system uses **TF-IDF (Term Frequency–Inverse Document Frequency)** to convert article text into numerical features. The configured vectorizer uses lowercase text, English stop-word removal, up to 50,000 features, a minimum document frequency of 2, unigrams and bigrams, and sublinear term-frequency scaling.

### Classification

The final classifier is **Logistic Regression**, configured with:

- Maximum iterations: 1,000
- Solver: `liblinear`
- Random state: 42

The TF-IDF vectorizer and classifier are combined in one scikit-learn Pipeline and saved as `fake_news_model.joblib`.

### Algorithm comparison

| Algorithm | Accuracy | Macro F1-score |
|---|---:|---:|
| Logistic Regression | **95.90%** | **95.87%** |
| Multinomial Naive Bayes | 88.87% | 88.80% |

Logistic Regression was selected because it achieved the higher scores in this experiment.

## 9. Model Evaluation

The final Logistic Regression model was evaluated on the held-out test set of 12,736 records.

### Overall results

| Metric | Result |
|---|---:|
| Accuracy | **95.90%** |
| Macro F1-score | **95.87%** |
| Correct predictions | 12,214 |
| Incorrect predictions | 522 |

### Class-wise results

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Fake | 96.21% | 96.29% | 96.25% |
| Real | 95.53% | 95.43% | 95.48% |

These figures describe performance on the held-out WELFake test set. They must not be presented as real-world fact-checking accuracy or as a guarantee of correct predictions on new articles.

## 10. Application Features

The implemented web application includes:

- A browser-based interface built with HTML, CSS and JavaScript.
- A Flask backend connected to the saved machine-learning pipeline.
- Headline and full-article input fields.
- Fake/Real classification output.
- Model confidence and class-probability estimates.
- Input validation for missing, incorrectly typed, excessively long and repetitive article text.
- A health-check API endpoint.
- A disclaimer explaining that the output is not factual verification.

The application runs locally and does not require a paid AI API or an external AI service to generate predictions.

## 11. Technology Stack

| Component | Technology | Role |
|---|---|---|
| Programming language | Python 3.11.9 | Main project language |
| Data handling | pandas, NumPy | Dataset processing |
| Machine learning | scikit-learn | TF-IDF and classification pipeline |
| Text representation | TF-IDF | Converts text into numerical features |
| Classification | Logistic Regression | Predicts the class |
| Model persistence | joblib | Saves and loads the fitted pipeline |
| Backend | Flask | Serves the interface and API endpoints |
| Frontend | HTML, CSS, JavaScript | User interface and interactions |
| Visualisation | Matplotlib, Seaborn | Evaluation plots |

## 12. Project Structure

The repository is organised into data-preparation, model-training, evaluation, documentation and web-application components.

```text
CAPSTONE/
├── audit_data.py
├── clean_data.py
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

The raw and cleaned datasets and the trained model artifact may be stored locally rather than committed to the repository. The web application expects `fake_news_model.joblib` in the project root.

## 13. Scope

### Included in the project

- Binary classification of English news text into Fake and Real dataset classes.
- Dataset auditing and cleaning.
- TF-IDF feature extraction.
- Logistic Regression training and evaluation.
- Comparison with Multinomial Naive Bayes.
- Saving and loading the trained model.
- Local Flask web application and JSON API endpoints.
- Input validation and responsible-use messaging.

### Outside the current scope

- Independent fact verification against trusted sources.
- Live news crawling or automatic source credibility checks.
- Verification of images, videos, audio or social-media accounts.
- Guaranteed detection of all misinformation.
- Headline-only classification.
- Support for languages other than the English news text represented in the training data.

## 14. Limitations and Responsible Use

The model learns statistical associations from the WELFake dataset. It may be influenced by dataset composition, label quality, source patterns and changes in writing style. Performance on a held-out random test split does not establish performance on every type of real-world news.

The probability shown by the application is a model estimate, not a measure of factual certainty. Users should verify important claims using multiple reliable and independent sources. VERITAS should not be the sole basis for trusting or rejecting an article, publisher or individual.

## 15. Future Scope

Possible future improvements, not part of the current implemented system, include:

- Evaluating the model on additional independent and more recent datasets.
- Studying performance across different topics, publishers and writing styles.
- Exploring additional classification algorithms and feature representations.
- Adding explainability tools to show which text features influenced a prediction.
- Investigating carefully sourced external evidence or fact-checking integrations.
- Improving multilingual support after obtaining suitable labelled datasets.

Any future extension should be tested carefully and should preserve a clear distinction between text-pattern classification and actual fact verification.

## 16. Conclusion

VERITAS demonstrates an end-to-end application of supervised machine learning to news text classification. It covers dataset auditing, data cleaning, TF-IDF feature extraction, Logistic Regression training, model evaluation, model persistence and deployment through a Flask web interface.

The project achieved 95.90% accuracy and a 95.87% macro F1-score on its held-out WELFake test set. These results demonstrate the model's performance on that dataset split, while also highlighting the importance of recognising dataset limitations and avoiding unsupported claims about real-world truth detection.

VERITAS is therefore presented as an educational AI tool for exploring text classification and responsible use of machine-learning predictions.
