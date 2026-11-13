
from pathlib import Path
import joblib

# Locate the existing trained model in the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "fake_news_model.joblib"

# Load the model once when the application starts
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


def predict_news(title="", article=""):
    """
    Predict whether news text resembles the Fake or Real
    class learned from the WELFake training dataset.
    """

    title = title.strip()
    article = article.strip()

    combined_text = f"{title} {article}".strip()

    if not combined_text:
        raise ValueError("Please provide a headline or article.")

    prediction = int(model.predict([combined_text])[0])
    probabilities = model.predict_proba([combined_text])[0]

    # Original WELFake label mapping: 0 = Fake, 1 = Real
    class_names = {
        0: "Fake",
        1: "Real"
    }

    confidence = float(
        probabilities[list(model.classes_).index(prediction)]
    )

    return {
        "prediction": prediction,
        "label": class_names[prediction],
        "confidence": round(confidence * 100, 2),
        "probabilities": {
            class_names[int(class_id)]: round(float(prob) * 100, 2)
            for class_id, prob in zip(model.classes_, probabilities)
        }
    }
