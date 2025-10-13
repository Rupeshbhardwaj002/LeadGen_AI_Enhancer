# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from model import train_and_predict_leads

# helper to embed local images
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(page_title="LeadGen AI Enhancer", layout="wide")
# embed images (ensure assets/logo.png and assets/background.jpg exist)
try:
    logo_b64 = get_base64_image("assets/logo.png")
    bg_b64 = get_base64_image("assets/background.png")
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    h1, h2, h3, h4, p, label {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex; align-items:center;">
        <img src="data:image/png;base64,{logo_b64}" width="90" style="margin-right:12px;">
        <h1>LeadGen AI Enhancer</h1>
    </div>
    """, unsafe_allow_html=True)
except Exception:
    st.title("LeadGen AI Enhancer (logo/background not loaded)")

st.markdown("Upload your SaaSquatchLeads CSV to clean, validate, and prioritize leads automatically.")
uploaded = st.file_uploader("Upload CSV", type=["csv"])

# Use sample_data.csv if no upload
input_source = uploaded if uploaded is not None else "sample_data.csv"

try:
    df_scored, model, scaler, feature_names = train_and_predict_leads(input_source)
except Exception as e:
    st.error(f"Error processing file: {e}")
    st.stop()

# Debug info (optional)
st.write("### Data preview (first rows)")
st.dataframe(df_scored.head())

# Download
csv_bytes = df_scored.to_csv(index=False).encode('utf-8')
st.download_button("💾 Download Scored CSV", csv_bytes, "scored_leads.csv", "text/csv")

# Histogram
if 'Lead_Score' in df_scored.columns:
    st.subheader("Lead Score Distribution")
    fig, ax = plt.subplots(figsize=(4,2))
    ax.hist(df_scored['Lead_Score'], bins=10)
    ax.set_xlabel("Lead Score")
    ax.set_ylabel("Count")
    st.pyplot(fig)
else:
    st.warning("Lead_Score missing in output.")

# Feature importance (use feature_names returned by model)
try:
    st.subheader("Feature Importance")
    coefs = model.coef_[0]
    # If model was trained on features matching feature_names, good, else attempt best-effort mapping.
    if len(coefs) >= len(feature_names):
        feat_df = pd.DataFrame({'Feature': feature_names, 'Importance': coefs[:len(feature_names)]})
    else:
        # fallback: create placeholder names
        feat_df = pd.DataFrame({'Feature': [f"f{i}" for i in range(len(coefs))], 'Importance': coefs})
    feat_df = feat_df.sort_values(by='Importance', ascending=False)
    fig2, ax2 = plt.subplots(figsize=(4,2))
    ax2.barh(feat_df['Feature'], feat_df['Importance'], color='orange')
    ax2.invert_yaxis()
    st.pyplot(fig2)
except Exception as ex:
    st.warning(f"Could not show feature importance: {ex}")

# Filter top leads
st.subheader("Filter Top Leads")
threshold = st.slider("Minimum lead score", 0, 20, 35)
df_filtered = df_scored[df_scored['Lead_Score'] >= threshold]
st.write(f"Showing {len(df_filtered)} leads with Lead_Score >= {threshold}")
st.dataframe(df_filtered)

# Summary stats
st.subheader("Summary")
if 'Lead_Score' in df_scored.columns:
    st.write(f"- Average: {df_scored['Lead_Score'].mean():.2f}")
    st.write(f"- Min: {df_scored['Lead_Score'].min():.2f}")
    st.write(f"- Max: {df_scored['Lead_Score'].max():.2f}")

# Sorting
st.subheader("Sort Leads")
sort_col = st.selectbox("Sort by", options=df_scored.columns.tolist(), index=df_scored.columns.get_loc('Lead_Score') if 'Lead_Score' in df_scored.columns else 0)
asc = st.checkbox("Ascending", value=False)
st.dataframe(df_scored.sort_values(by=sort_col, ascending=asc))
