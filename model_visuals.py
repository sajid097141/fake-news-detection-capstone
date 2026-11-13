
import matplotlib.pyplot as plt
import numpy as np

# Model comparison results
models = ["Logistic Regression", "Multinomial Naive Bayes"]
accuracy = [95.90, 88.87]
macro_f1 = [95.87, 88.80]

# Graph 1: Model comparison
x = np.arange(len(models))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))

bars1 = ax.bar(x - width/2, accuracy, width, label="Accuracy")
bars2 = ax.bar(x + width/2, macro_f1, width, label="Macro F1")

ax.set_ylabel("Score (%)")
ax.set_title("Machine Learning Model Performance Comparison")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.set_ylim(0, 110)
ax.legend()

ax.bar_label(bars1, fmt="%.2f%%", padding=3)
ax.bar_label(bars2, fmt="%.2f%%", padding=3)

plt.tight_layout()
plt.savefig("model_comparison.png", dpi=300)
plt.show()

# Graph 2: Class-wise performance
metrics = ["Precision", "Recall", "F1-score"]

# WELFake labels: 0 = Fake, 1 = Real
real = [95.53, 95.43, 95.48]
fake = [96.21, 96.29, 96.25]

x = np.arange(len(metrics))

fig, ax = plt.subplots(figsize=(8, 5))

bars1 = ax.bar(x - width/2, real, width, label="Real")
bars2 = ax.bar(x + width/2, fake, width, label="Fake")

ax.set_ylabel("Score (%)")
ax.set_title("Class-wise Classification Performance")
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 110)
ax.legend()

ax.bar_label(bars1, fmt="%.2f%%", padding=3)
ax.bar_label(bars2, fmt="%.2f%%", padding=3)

plt.tight_layout()
plt.savefig("results/class_performance_corrected.png", dpi=300)
plt.show()

print("Both graphs saved successfully!")
