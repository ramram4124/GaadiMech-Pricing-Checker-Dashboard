import pandas as pd
import re

# Load the dataset
df = pd.read_csv('car_dekho_jaipur.csv')  # Replace 'your_file_name.csv' with your actual file name

# 1. Standardize Units and Formats
# Remove currency symbols and convert to float
df['actual price'] = df['actual price'].str.replace(r'Rs\.|₹', '', regex=True).str.strip().astype(float)
df['discounted price'] = df['discounted price'].str.replace('₹', '', regex=True).str.strip().astype(float)

# Convert time to hours
def convert_to_hours(time_str):
    if pd.isna(time_str):  # Handle NaN values
        return None
    time_str = time_str.lower()
    if 'day' in time_str:
        days = float(re.search(r'\d+', time_str).group())
        return days * 24
    elif 'hour' in time_str or 'hr' in time_str:
        return float(re.search(r'\d+', time_str).group())
    else:
        return None  # For cases where no time is specified

df['time taken'] = df['time taken'].apply(convert_to_hours)

# 2. Handle Missing Data
# This step might need manual review or imputation based on similar services

# 3. Text Cleaning
# Split recommendations into structured format
def parse_recommendations(rec):
    if pd.isna(rec):
        return {'Warranty': '', 'Interval': '', 'Condition': ''}
    items = rec.split('•')
    warranty = ''
    interval = ''
    condition = ''
    for item in items:
        if 'Warranty' in item:
            warranty = item.strip()
        elif 'Month' in item or 'Year' in item or 'Kms' in item:
            interval = item.strip()
        else:
            condition = item.strip()
    return {'Warranty': warranty, 'Interval': interval, 'Condition': condition}

recommendation_df = df['recommendation'].apply(parse_recommendations).apply(pd.Series)
df = pd.concat([df, recommendation_df], axis=1)
df.drop(columns=['recommendation'], inplace=True)

# 4. Data Type Conversion
# Already handled with price and time conversions

# 5. Correct Typos and Inconsistencies
# This would require manual checking or a more sophisticated NLP approach

# 6. Normalization of Car Names
# Assuming car names are already consistent, but here's how to clean if needed
df['car'] = df['car'].str.lower().str.replace('-', ' ')

# 7. Duplicate Entries
df.drop_duplicates(inplace=True)

# 8. Categorical Data
# If needed for further analysis, you might encode 'service category'
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['service category'] = le.fit_transform(df['service category'])

# 9. Missing Service Times
# You might want to impute or flag these for review
df['time taken'] = df['time taken'].fillna(df['time taken'].mean())

# 10. Validation Checks
df = df[df['discounted price'] <= df['actual price']]

# Save the cleaned dataset
df.to_csv('cleaned_dataset.csv', index=False)