# Model Documentation

## 1. Model Overview

VERITAS uses a supervised machine-learning text-classification model to classify a news article as **Fake** or **Real** based on patterns learned from the WELFake dataset.

The selected model is a scikit-learn Pipeline consisting of:

1. **TF-IDF Vectorizer** — converts the input text into numerical features.
2. **Logistic Regression classifier** — uses those features to predict one of the two classes.

The complete fitted pipeline is saved as `fake_news_model.joblib` and loaded by the Flask application for predictions.

> **Scope:** This is a text-pattern classification model. It does not independently fact-check claims, verify sources, or determine objective truth.

## 2. Dataset

### WELFake Dataset

The project uses the WELFake dataset, which contains news articles labelled as Fake or Real.

- Dataset: WELFake
- Source: [WELFake dataset on Zenodo](https://zenodo.org/records/4561253)
- Original records: **72,134**
- Records after cleaning: **63,676**
- Input text: news title and article body
- Target column: `label`

### Label mapping

| Label value | Class |
|---:|---|
| 0 | Fake |
| 1 | Real |

This label convention is retained throughout training, evaluation, and prediction.

## 3. Data Preparation

The data preparation process is implemented in `audit_data.py` and `clean_data.py`.

### Audit

The initial audit checks:

- Dataset dimensions
- Missing values
- Exact duplicate rows
- Empty combined text
- Duplicate article text
- Duplicate text with conflicting labels

### Cleaning steps

1. Load `WELFake_Dataset.csv`.
2. Remove the unnecessary `Unnamed: 0` index column.
3. Replace missing title and article values with empty strings.
4. Combine the title and article body into a `combined_text` field.
5. Remove records where the combined text is empty.
6. Remove duplicate combined text entries, keeping the first occurrence.
7. Reset the DataFrame index.
8. Save the cleaned data as `cleaned_WELFake.csv`.

The final cleaned dataset contains **63,676 records**.

## 4. Training and Test Split

The dataset is divided using scikit-learn's `train_test_split`.

| Setting | Value |
|---|---:|
| Test size | 20% |
| Training size | 80% |
| Random state | 42 |
| Stratification | Enabled |
| Training records | 50,940 |
| Testing records | 12,736 |

Stratification preserves the class proportions across the training and testing subsets.

The split is performed before TF-IDF vectorisation. Since the vectorizer is part of the Pipeline, it is fitted on the training data during model training and then applied to the test data.

## 5. Feature Extraction: TF-IDF

The model uses **Term Frequency–Inverse Document Frequency (TF-IDF)** to convert text into numerical features.

TF-IDF gives greater importance to words that are informative within a document while reducing the influence of words that appear very frequently across the collection.

The configured `TfidfVectorizer` parameters are:

| Parameter | Value | Purpose |
|---|---|---|
| `lowercase` | `True` | Converts text to lowercase. |
| `stop_words` | `"english"` | Removes built-in English stop words. |
| `max_features` | `50000` | Limits the vocabulary to at most 50,000 features. |
| `min_df` | `2` | Ignores terms appearing in fewer than two documents in the fitting data. |
| `ngram_range` | `(1, 2)` | Uses unigrams and bigrams. |
| `sublinear_tf` | `True` | Applies sublinear scaling to term frequency. |

### Unigrams and bigrams

- **Unigrams** are individual words.
- **Bigrams** are pairs of consecutive words.

Using both allows the model to learn from individual terms as well as short word combinations.

## 6. Classification Algorithm: Logistic Regression

Logistic Regression is a supervised classification algorithm used here to distinguish between two classes: Fake and Real.

After TF-IDF converts the article into a feature vector, Logistic Regression estimates the probability of each class and selects the class with the higher predicted probability.

The configured parameters are:

| Parameter | Value |
|---|---|
| `max_iter` | `1000` |
| `solver` | `"liblinear"` |
| `random_state` | `42` |

The model is implemented inside a scikit-learn `Pipeline`, keeping feature extraction and classification together.

## 7. Model Comparison

Two algorithms were evaluated using the same stratified 80:20 train-test split and TF-IDF configuration.

| Model | Accuracy | Macro F1-score |
|---|---:|---:|
| Logistic Regression | **95.90%** | **95.87%** |
| Multinomial Naive Bayes | 88.87% | 88.80% |

Logistic Regression achieved the higher accuracy and macro F1-score in this experiment. It was therefore selected as the final classifier used by VERITAS.

The comparison is implemented in `compare_models.py`.

## 8. Final Model Evaluation

The selected Logistic Regression model was evaluated on the held-out test set of 12,736 records.

### Overall results

| Metric | Result |
|---|---:|
| Test records | 12,736 |
| Correct predictions | 12,214 |
| Incorrect predictions | 522 |
| Accuracy | **95.90%** |
| Macro F1-score | **95.87%** |

### Class-wise performance

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Fake | 96.21% | 96.29% | 96.25% |
| Real | 95.53% | 95.43% | 95.48% |

### Metric definitions

- **Accuracy:** Proportion of all test predictions that were correct.
- **Precision:** Of the items predicted as a particular class, the proportion that actually belonged to that class.
- **Recall:** Of the items that actually belonged to a particular class, the proportion correctly identified.
- **F1-score:** Harmonic mean of precision and recall.
- **Macro F1-score:** Average of the F1-scores of the two classes, giving each class equal weight.

The evaluation script is `evaluate_model.py`. It generates a classification report and saves a confusion-matrix visualisation to `results/confusion_matrix_corrected.png`.

## 9. Saving and Loading the Model

After training, the complete Pipeline is saved using joblib:

```python
joblib.dump(model, "fake_news_model.joblib")
```

The web application's `predictor.py` loads the saved file once when the module is imported:

```python
model = joblib.load(MODEL_PATH)
```

The model file is expected at the project root, one directory above the `webapp` folder.

Saving the complete Pipeline means the application uses the same fitted TF-IDF transformation and Logistic Regression classifier that were trained together. A separate vectorizer does not need to be fitted at prediction time.

## 10. Prediction Process

When the application receives a title and article:

1. The title and article are stripped of surrounding whitespace.
2. They are combined into one text string.
3. The saved Pipeline transforms the text using its fitted TF-IDF vectorizer.
4. Logistic Regression predicts the class.
5. The model's class probabilities are retrieved using `predict_proba()`.
6. The class ID is mapped to its label: `0 = Fake`, `1 = Real`.
7. The application returns the predicted label, confidence percentage, and probabilities for both classes.

The confidence percentage is the model probability associated with the predicted class. It should not be interpreted as factual certainty.

## 11. Limitations

The evaluation results describe performance on a held-out portion of the WELFake dataset. They do not guarantee the same performance on live news, new topics, different publishers, or future events.

Important limitations include:

- The model learns statistical language patterns from its training data; it does not verify claims against evidence.
- It does not independently assess the reliability of a publisher or author.
- Dataset biases, duplicated patterns, and changes in writing style may affect predictions.
- A model probability is not proof that a news report is true or false.
- The model was trained using combined title and article text. VERITAS therefore requires the full article for predictions; headline-only predictions are disabled.

VERITAS should be used as an educational demonstration of text classification, not as a replacement for professional journalism, source verification, or independent fact-checking.

## 12. Reproducibility

The main scripts associated with the model workflow are:

| File | Purpose |
|---|---|
| `audit_data.py` | Inspects the original dataset for data-quality issues. |
| `clean_data.py` | Cleans the dataset and creates `cleaned_WELFake.csv`. |
| `compare_models.py` | Compares Logistic Regression and Multinomial Naive Bayes. |
| `train_model.py` | Trains, evaluates, and saves the final Pipeline. |
| `evaluate_model.py` | Evaluates the saved model and creates a confusion-matrix visualisation. |
| `inspect_saved_model.py` | Inspects the saved model artifact. |
| `model_results.txt` | Stores the recorded final evaluation summary. |

The project uses Python and the libraries listed in the repository's `requirements.txt`.
