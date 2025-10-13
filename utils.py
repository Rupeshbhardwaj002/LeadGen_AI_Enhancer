import pandas as pd
import re
from email_validator import validate_email, EmailNotValidError

def clean_email(email):
    if pd.isna(email):
        return ""
    email = email.strip().lower()
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        try:
            validate_email(email)
            return email
        except EmailNotValidError:
            return ""
    return ""

def clean_data(df):
    df = df.drop_duplicates()
    if 'email' in df.columns:
        df['email'] = df['email'].apply(clean_email)
        df = df[df['email'] != ""]

    df = df.fillna({
        'industry': 'Unknown',
        'title': 'Unknown',
        'company_size': 'Small'
    })
    return df
