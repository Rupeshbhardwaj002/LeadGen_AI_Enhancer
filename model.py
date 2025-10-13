# model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import re

def _simple_text_features(df):
    """
    Create simple numeric features from text columns if dataset lacks numeric columns.
    - has_email : whether an email-like string exists
    - title_is_ceo : title contains 'ceo'
    - title_is_manager : title contains 'manager'
    - company_len : length of company string
    """
    out = pd.DataFrame(index=df.index)

    # has_email: look for a column that looks like email or an email-like token anywhere
    email_mask = False
    for c in df.columns:
        if df[c].astype(str).str.contains(r'@', na=False).any():
            out['has_email'] = df[c].astype(str).str.contains(r'@', na=False).astype(int)
            email_mask = True
            break
    if not email_mask:
        out['has_email'] = 0

    # title derived features
    title_col = None
    for c in df.columns:
        if 'title' in c.lower():
            title_col = c
            break
    if title_col is not None:
        title = df[title_col].astype(str).str.lower()
        out['title_is_ceo'] = title.str.contains('ceo|founder|chief', na=False).astype(int)
        out['title_is_manager'] = title.str.contains('manager|head|lead|director', na=False).astype(int)
    else:
        out['title_is_ceo'] = 0
        out['title_is_manager'] = 0

    # company length feature
    company_col = None
    for c in df.columns:
        if 'company' in c.lower() or 'org' in c.lower():
            company_col = c
            break
    if company_col is not None:
        out['company_len'] = df[company_col].astype(str).str.len().fillna(0)
    else:
        out['company_len'] = 0

    # fallback: number of non-empty text columns per row (proxy for richness)
    out['text_nonempty_count'] = df.apply(lambda r: r.astype(str).replace('nan','').map(len).gt(0).sum(), axis=1)

    return out

def train_and_predict_leads(file_like):
    """
    Read uploaded CSV (file path or file-like), create features automatically,
    train logistic regression (using synthetic target if necessary), and return
    scored DataFrame, trained model, scaler, and feature_names list.
    """

    # Read CSV robustly (file-like object or path str)
    if hasattr(file_like, "read"):
        # Streamlit passes UploadedFile object; pandas can read it directly
        df_raw = pd.read_csv(file_like)
    else:
        df_raw = pd.read_csv(str(file_like))

    # Basic safety checks
    if df_raw is None or df_raw.shape[0] == 0:
        raise ValueError("Uploaded file is empty or unreadable.")

    # Keep original copy to attach Lead_Score later
    df_original = df_raw.copy()

    # Select numeric columns
    numeric_df = df_raw.select_dtypes(include=[np.number]).copy()

    if numeric_df.shape[1] >= 1:
        # Use numeric columns as features
        X = numeric_df.copy()
        # if 'Converted' exists, use as y
        if 'Converted' in numeric_df.columns:
            y = numeric_df['Converted'].astype(int)
            X = numeric_df.drop(columns=['Converted'])
        else:
            # create synthetic target: higher-sum rows labeled 1
            row_sum = X.sum(axis=1)
            y = (row_sum > row_sum.median()).astype(int)
    else:
        # No numeric columns: create simple text-derived numeric features
        X = _simple_text_features(df_raw)
        row_sum = X.sum(axis=1)
        y = (row_sum > row_sum.median()).astype(int)

    # Ensure no NaNs
    X = X.fillna(0)
    y = pd.to_numeric(y, errors='coerce').fillna(0).astype(int)

    # Keep feature names for later visualization
    feature_names = list(X.columns)

    # Scale numeric features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train logistic regression (simple default)
    # If dataset is tiny, still works
    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)

    # Predict probabilities for all rows
    probs = model.predict_proba(X_scaled)[:, 1]
    lead_scores = (probs * 100).round(2)

    # Attach to original dataframe (preserve original columns)
    df_original = df_original.reset_index(drop=True)
    df_original['Lead_Score'] = lead_scores

    # Return full df with Lead_Score, model, scaler, and feature_names
    return df_original, model, scaler, feature_names
