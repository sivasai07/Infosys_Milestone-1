import pandas as pd
from preprocess_data import load_data, clean_data

data_path = "data/clean_data.csv"

df = load_data(data_path)
df = clean_data(df)

print("\nBasic Info:")
print(df.info())

print("\nSummary Statistics:")
print(df.describe())

print("\nMissing Values:")
print(df.isnull().sum())
