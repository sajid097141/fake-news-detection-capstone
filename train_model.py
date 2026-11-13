
import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# 1. Load cleaned dataset
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "cleaned_WELFake.csv")

X = df["combined_text"].fillna("")
y = df["label"]

# 2. Split data before vectorisation
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# 3. Build ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_features=50000,
        min_df=2,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        solver="liblinear",
        random_state=42
    ))
])

# 4. Train model
print("\nTraining model...")
model.fit(X_train, y_train)

# 5. Evaluate model
print("\nEvaluating model...")
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Fake", "Real"],  # WELFake labels: 0 = Fake, 1 = Real
    digits=4
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 6. Save trained model
model_path = BASE_DIR / "fake_news_model.joblib"
joblib.dump(model, model_path)

print("\nModel saved to:", model_path)
