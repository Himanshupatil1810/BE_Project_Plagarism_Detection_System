import pandas as pd

# Load both CSV files
df1 = pd.read_csv("wiki_train_pairs.csv")
df2 = pd.read_csv("train_pairs.csv")

# Merge (append rows)
merged = pd.concat([df1, df2], ignore_index=True)

# Remove duplicates (optional)
merged = merged.drop_duplicates()

# Shuffle rows (optional but recommended)
merged = merged.sample(frac=1, random_state=42).reset_index(drop=True)

# Save merged file
merged.to_csv("merged_pairs.csv", index=False)

print("✅ Merged successfully!")
print("Total rows:", len(merged))
