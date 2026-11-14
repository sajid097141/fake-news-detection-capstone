# VERITAS — Model Documentation

## 1. Model purpose

VERITAS uses supervised machine learning to classify English news text into the Fake or Real labels represented in the WELFake training dataset.

The model learns statistical associations in the training data. It does not verify claims, identify the original publisher's intent, or establish factual truth.

## 2. Dataset

- **Name:** WELFake
- **Source:** https://zenodo.org/records/4561253
- **Original records:** 72,134
- **Records after cleaning:** 63,676
- **Training records:** 50,940
- **Held-out test records:** 12,736
- **Split:** 80% training / 20% testing
- **Random state:** 42
- **Stratification:** by label

### Label mapping

| Numeric label | Class |
|---:|---|
| 0 | Fake |
| 1 | Real |

The model training input uses the article title and body joined into a single text field.

## 3. Text representation

The selected pipeline uses Term Frequency–Inverse Document Frequency (TF-IDF) to convert text into numerical features. The documented feature configuration uses unigrams and bigrams.

- **Unigram:** a single token.
- **Bigram:** a sequence of two adjacent tokens.

The fitted vectorizer is stored with the classifier in the saved scikit-learn pipeline.

## 4. Classification algorithm

**Logistic Regression** is the selected classification algorithm. It predicts one of the two WELFake classes and provides class-probability estimates through the scikit-learn pipeline.

The saved artifact is `fake_news_model.joblib`, loaded by `webapp/predictor.py` from the repository root.

## 5. Evaluation results

The selected model was evaluated on the held-out test set of 12,736 records.

### Overall performance

| Metric | Result |
|---|---:|
| Accuracy | **95.90%** |
| Macro F1-score | **95.87%** |
| Correct predictions | 12,214 |
| Incorrect predictions | 522 |

### Class-wise performance

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Fake | 96.21% | 96.29% | **96.25%** |
| Real | 95.53% | 95.43% | **95.48%** |

### Model comparison

| Model | Accuracy | Macro F1-score |
|---|---:|---:|
| Logistic Regression (selected) | **95.90%** | **95.87%** |
| Multinomial Naive Bayes | 88.87% | 88.80% |

These figures describe performance on the stated WELFake test split. They are not measurements of real-world truth detection or guaranteed performance on newly submitted articles.

## 6. Prediction flow

1. Trim the submitted headline and article.
2. Join them into a single text string.
3. Call the saved pipeline's `predict()` method.
4. Call `predict_proba()` to obtain class-probability estimates.
5. Map numeric class 0 to Fake and class 1 to Real.
6. Return the predicted class, label, confidence estimate, and probability estimates for both classes.

The application requires full article text. It rejects empty or very short article bodies and applies basic checks for repetitive input.

## 7. Understanding confidence

The displayed confidence is the model's probability estimate for its predicted class. It is not a calibrated guarantee, a source reliability score, or a probability that the article is factually true.

A high-confidence prediction can still be wrong, particularly when submitted text differs from the training distribution or contains patterns that the model learned as misleading signals.

## 8. Limitations

- The model depends on the coverage, labels, and potential biases of WELFake.
- A held-out random split may not represent future news or changing writing styles.
- The classifier may learn source, topic, or stylistic correlations instead of factual relationships.
- Performance may differ on other languages, short text, social posts, satire, or specialised domains.
- Model probabilities should not be interpreted as factual certainty.
- The model does not browse the web or consult external evidence as part of its prediction.

## 9. Relationship to VERITAS 2.0 evidence sources

The Google Fact Check Tools and GDELT components are separate evidence-retrieval paths. Their results do not modify the model's predicted label or confidence. Fact-check relevance is determined by a lexical-overlap heuristic and GDELT returns matching coverage; neither is a semantic or independent truth-verification engine.
