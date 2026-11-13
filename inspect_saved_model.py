
import joblib
import sklearn
from pathlib import Path

model_path = Path(__file__).parent / "fake_news_model.joblib"

print("Scikit-learn version:", sklearn.__version__)
print("Joblib version:", joblib.__version__)

model = joblib.load(model_path)

print("\nMODEL INSPECTION")
print("-------------------------")
print("Pipeline steps:", model.named_steps.keys())
print("Model classes:", model.classes_)

tfidf = model.named_steps["tfidf"]
classifier = model.named_steps["classifier"]

print("Vocabulary size:", len(tfidf.vocabulary_))
print("N-gram range:", tfidf.ngram_range)
print("Maximum features:", tfidf.max_features)
print("Classifier:", type(classifier).__name__)
print("Coefficient shape:", classifier.coef_.shape)

print("\nMODEL LOAD SUCCESSFUL")
