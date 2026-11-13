
import joblib

model = joblib.load("fake_news_model.joblib")

print("FAKE NEWS DETECTION SYSTEM")
print("Enter 'exit' to quit.")

while True:
    news = input("\nEnter news headline/article: ")

    if news.lower() == "exit":
        break

    prediction = model.predict([news])[0]
    probabilities = model.predict_proba([news])[0]

    confidence = max(probabilities) * 100

    # WELFake labels: 0 = Fake, 1 = Real
    if prediction == 0:
        result = "POTENTIALLY MISLEADING"
    else:
        result = "POTENTIALLY RELIABLE"

    print("\nPrediction:", result)
    print(f"Model confidence: {confidence:.2f}%")
