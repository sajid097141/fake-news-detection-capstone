
import pandas as pd

# Load dataset
df = pd.read_csv("WELFake_Dataset.csv")

print("Original records:", len(df))

# Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"])

# Handle missing values
df["title"] = df["title"].fillna("")
df["text"] = df["text"].fillna("")

# Combine title and article text
df["combined_text"] = (
    df["title"].str.strip() + " " +
    df["text"].str.strip()
).str.strip()

# Remove empty records
df = df[df["combined_text"] != ""]

# Remove duplicate combined texts
df = df.drop_duplicates(
    subset=["combined_text"],
    keep="first"
)

# Reset index
df = df.reset_index(drop=True)

# Save cleaned dataset
df.to_csv("cleaned_WELFake.csv", index=False)

print("\nCLEANING COMPLETED")
print("Final records:", len(df))

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSaved as cleaned_WELFake.csv")
