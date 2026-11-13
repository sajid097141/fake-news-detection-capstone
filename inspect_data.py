
import pandas as pd
from pathlib import Path

# Get the directory containing this Python file
BASE_DIR = Path(__file__).resolve().parent

# Dataset location
DATASET_PATH = BASE_DIR / "WELFake_Dataset.csv"

if not DATASET_PATH.exists():
    print("Dataset not found!")
    print("Expected location:", DATASET_PATH)
    raise SystemExit

df = pd.read_csv(DATASET_PATH)

print("Dataset Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nClass Distribution:")
print(df["label"].value_counts())

print("\nSample Records:")
print(df.head())
