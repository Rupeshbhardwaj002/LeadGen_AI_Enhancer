# model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import re


def _extract_basic_text_features(df):
    """
    Generate lightweight numeric features from text columns.
    Helps when no numeric data is available.
    """
    result = pd.DataFrame(index=df.index)

    # Check email-like strings
    email_found = False
    for col in df.columns:
        if df[col].astype(str).str.contains(r'@', na=False).any():
            result['has_email'] = df[col].astype(str).str.contains(r'@', na=False).astype(int)
            email_found = True
            break
    if not email_found:
        result['has_email'] = 0

    #possible title column
    title_col = next((c for c in df.columns if 'title' in c.lower()), None)
    if title_col:
        title_series = df[title_col].astype(str).str.lower()
        result['is_ceo_title'] = title_series.str.contains(r'ceo|founder|chief', na=False).astype(int)
        result['is_manager_title'] = title_series.str.contains(r'manager|head|lead|director', na=False).astype(int)
    else:
        result['is_ceo_title'] = 0
        result['is_manager_title'] = 0

    # Company length
    company_col = next((c for c in df.columns if 'company' in c.lower() or 'org' in c.lower()), None)
    if company_col:
        result['company_name_len'] = df[company_col].astype(str).str.len().fillna(0)
    else:
        result['company_name_len'] = 0

    #how many text fields are non-empty per row
    result['nonempty_text_fields'] = df.apply(
        lambda row: row.astype(str).replace('nan', '').map(len).gt(0).sum(),
        axis=1
    )

    return result


def train_and_predict_leads(file_path_or_buffer):
    """
    Reads uploaded CSV, builds features automatically,
    trains a logistic regression model, and returns:
      - DataFrame with Lead_Score
      - trained model
      - scaler
      - feature names
    """

    # Load CSV safely
    if hasattr(file_path_or_buffer, "read"):
        df_input = pd.read_csv(file_path_or_buffer)
    else:
        df_input = pd.read_csv(str(file_path_or_buffer))

    if df_input.empty:
        raise ValueError("Uploaded file appears empty or unreadable.")

    df_original = df_input.copy()

    # Select numeric columns safely
    numeric_data = df_input.select_dtypes(include=[np.number]).copy()

    if not numeric_data.empty:
        X = numeric_data.copy()
        if 'Converted' in X.columns:
            y = X['Converted'].astype(int)
            X = X.drop(columns=['Converted'])
        else:
            row_sums = X.sum(axis=1)
            y = (row_sums > row_sums.median()).astype(int)
    else:
        # Create numeric features from text
        X = _extract_basic_text_features(df_input)
        row_sums = X.sum(axis=1)
        y = (row_sums > row_sums.median()).astype(int)

    # Clean data
    X = X.fillna(0)
    y = pd.to_numeric(y, errors='coerce').fillna(0).astype(int)

    # Save feature names
    inputFeatures = list(X.columns)

    # Standardize features
    sclaer_data = StandardScaler()
    X_scaled = sclaer_data.fit_transform(X)

    # Train logistic regression
    lead_model = LogisticRegression(max_iter=1000)
    lead_model.fit(X_scaled, y)

    # Predict lead scores
    probabilities = lead_model.predict_proba(X_scaled)[:, 1]
    lead_scores = (probabilities * 100).round(2)

    # Attach to original dataframe
    df_original = df_original.reset_index(drop=True)
    df_original['Lead_Score'] = lead_scores

    # Return all artifacts
    return df_original, lead_model, sclaer_data, inputFeatures
