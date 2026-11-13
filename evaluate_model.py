
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

df = pd.read_csv("cleaned_WELFake.csv")

X = df["combined_text"].fillna("")
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = joblib.load("fake_news_model.joblib")

predictions = model.predict(X_test)

# Confusion matrix
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(7, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Greens",
    xticklabels=["Fake", "Real"],   # WELFake labels: 0 = Fake, 1 = Real
    yticklabels=["Fake", "Real"] 
)

plt.title("Fake News Detection - Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.tight_layout()
plt.savefig("results/confusion_matrix_corrected.png", dpi=300)
plt.show()

# Classification report
print("\nCLASSIFICATION REPORT")
print(classification_report(
    y_test,
    predictions,
    target_names=["Fake", "Real"],
    digits=4
))

print("\nGraph saved as results/confusion_matrix_corrected.png")
