# VERITAS — Project Overview

## 1. Project summary

**VERITAS — AI-Powered Fake News Detection System** is a CBSE Class XII Artificial Intelligence capstone project. It analyses English news articles using a machine-learning classifier trained on labelled examples from the WELFake dataset. The web application also provides optional external context through published fact-check reviews and recent news-coverage search.

VERITAS does not independently establish whether a news claim is true or false. Its ML component identifies patterns associated with the dataset's Fake and Real labels.

## 2. Problem statement

Readers encounter large amounts of online news and may find it difficult to assess unfamiliar articles. A text classifier can demonstrate how machine learning identifies patterns in labelled examples, while external search services can help users locate existing fact-check reviews and related reporting.

The project demonstrates these capabilities while clearly communicating their limitations.

## 3. Objectives

- Build a machine-learning pipeline that classifies article text into the Fake or Real classes learned from WELFake.
- Develop a browser-based interface using HTML, CSS, and JavaScript.
- Provide a Flask backend and JSON API.
- Retrieve existing fact-check reviews through Google Fact Check Tools.
- Label returned claims by lexical overlap with the submitted search query.
- Retrieve recent matching news articles through GDELT DOC 2.0.
- Keep ML predictions independent from external evidence and handle external-service failures gracefully.
- Explain model uncertainty, relevance-filter limitations, and privacy considerations to users.

## 4. Main features

- Headline and full-article input.
- Input validation and repetitive-text checks.
- TF-IDF + Logistic Regression prediction with class-probability estimates.
- Fact-check review search with direct-match, related, and irrelevant lexical labels.
- Recent news-coverage search.
- Unified analysis response with independent evidence statuses.
- Legacy ML-only prediction endpoint.
- Privacy notice and prominent model disclaimer.

## 5. Technology stack

| Component | Technology |
|---|---|
| Programming language | Python 3.11 |
| Backend | Flask |
| Machine learning | scikit-learn |
| Text features | TF-IDF, unigrams and bigrams |
| Classifier | Logistic Regression |
| Model persistence | joblib |
| Dataset processing | pandas, NumPy, SciPy |
| Frontend | HTML, CSS, JavaScript |
| Fact-check search | Google Fact Check Tools API |
| News-coverage search | GDELT DOC 2.0 |
| Automated tests | Python unittest and unittest.mock |

## 6. Dataset and model

The classifier was trained using the WELFake dataset. The label mapping is:
- `0` — Fake
- `1` — Real

The selected model is a scikit-learn pipeline containing TF-IDF feature extraction and Logistic Regression. The web application combines the headline and article body before prediction.

The README records held-out WELFake test results of 95.90% accuracy and 95.87% macro F1-score on 12,736 test records. These are dataset evaluation metrics, not real-world fact-checking accuracy.

## 7. How a user request is processed

1. The user enters a headline and full article.
2. The Flask backend validates the request and article text.
3. The local model returns a Fake/Real class prediction and probability estimates.
4. The application separately queries Google Fact Check Tools and GDELT using the headline, or a shortened article query when no headline is provided.
5. Fact-check results are annotated using a lexical-overlap heuristic.
6. The API returns the ML result and each external evidence stream with its own status.
7. The interface presents the results and limitations.

## 8. Limitations

- The model learns dataset-specific text patterns and may reflect dataset bias.
- Probability estimates are not guarantees of correctness.
- The lexical relevance filter is a simple word-overlap heuristic, not semantic reasoning.
- Fact-check results depend on reviews already indexed by the external service.
- GDELT results show matching coverage, not proof of truth.
- External services may return no results, become unavailable, or apply rate limits.
- The current workflow accepts pasted text; URL extraction is not part of this version.
- The system is intended for English news text and educational demonstration.

## 9. Project identity

**Project:** VERITAS — AI-Powered Fake News Detection System  
**Subject:** Artificial Intelligence (843)  
**Level:** CBSE Class XII Capstone  
**Author:** Sajid Ekbal Choudhury  
**School:** PM SHRI Kendriya Vidyalaya 210 CoBRA CRPF Dalgaon, Assam  
**Academic year:** 2026–27
