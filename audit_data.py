
import pandas as pd

df = pd.read_csv("WELFake_Dataset.csv")

print("INITIAL SHAPE:", df.shape)

# Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"])

# Inspect missing values
print("\nMISSING VALUES:")
print(df.isnull().sum())

# Inspect duplicate rows
print("\nEXACT DUPLICATE ROWS:")
print(df.duplicated().sum())

# Prepare combined text for duplicate inspection
df["title"] = df["title"].fillna("")
df["text"] = df["text"].fillna("")

df["combined_text"] = (
    df["title"].str.strip() + " " +
    df["text"].str.strip()
).str.strip()

print("\nEMPTY ARTICLES:")
print((df["combined_text"] == "").sum())

print("\nDUPLICATE TEXTS:")
print(df["combined_text"].duplicated().sum())

# Check whether identical text has conflicting labels
label_counts = df.groupby("combined_text")["label"].nunique()

print("\nDUPLICATE TEXTS WITH CONFLICTING LABELS:")
print((label_counts > 1).sum())

print("\nFINAL AUDIT COMPLETED.")
