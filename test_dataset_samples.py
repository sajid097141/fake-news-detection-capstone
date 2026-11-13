
import pandas as pd
import joblib

df = pd.read_csv("cleaned_WELFake.csv")
model = joblib.load("fake_news_model.joblib")

# Select 5 records from each class
samples = pd.concat([
    df[df["label"] == 0].sample(5, random_state=42),
    df[df["label"] == 1].sample(5, random_state=42)
])

for _, row in samples.iterrows():

    text = row["combined_text"]

    actual = "FAKE" if row["label"] == 0 else "REAL"
    prediction = model.predict([text])[0]
    predicted = "FAKE" if prediction == 0 else "REAL"

    confidence = max(model.predict_proba([text])[0]) * 100

    print("\n" + "=" * 60)
    print("NEWS:", text[:300])
    print("ACTUAL:", actual)
    print("PREDICTED:", predicted)
    print(f"CONFIDENCE: {confidence:.2f}%")
    print("RESULT:", "CORRECT" if actual == predicted else "INCORRECT")
