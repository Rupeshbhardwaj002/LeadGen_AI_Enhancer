# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from model import train_and_predict_leads  # importing model

#helper to embed local images[logo and backgr..]
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Streamlit page setup ->
st.set_page_config(page_title="LeadGen AI Enhancer", layout="wide")

# Trying loading visuals 
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
    st.title("LeadGen AI Enhancer (Visuals Missing)")

# Upload area
st.markdown("Upload your SaaSquatchLeads CSV to clean, validate, and prioritize leads automatically.")
user_uploaded = st.file_uploader("Upload CSV file", type=["csv"])

# using sample data if nothing uploaded
source_path = user_uploaded if user_uploaded is not None else "sample_data.csv"

#Running model
try:
    final_scored_leads, lead_model, scaler_data, inputFeatures = train_and_predict_leads(source_path)
except Exception as e:
    st.error(f"Error while processing file: {e}")
    st.stop()

#Display first few rows
st.write("### 🧾 Data preview")
st.dataframe(final_scored_leads.head())

#Downloadbutoon for downloading CSV
csv_data = final_scored_leads.to_csv(index=False).encode('utf-8')
st.download_button("💾 Download Scored Leads", csv_data, "scored_leads.csv", "text/csv")

# Histogram code (Lead Score Distribution)
if 'Lead_Score' in final_scored_leads.columns:
    st.subheader("Lead Score Distribution")
    hist_fig, hist_ax = plt.subplots(figsize=(4, 2))
    hist_ax.hist(final_scored_leads['Lead_Score'], bins=10, color='skyblue', edgecolor='black')
    hist_ax.set_xlabel("Lead Score")
    hist_ax.set_ylabel("Count")
    st.pyplot(hist_fig)
else:
    st.warning("Lead_Score column missing, skipping histogram.")

#Feature Importance Plot
try:
    st.subheader("Feature Importance (from Logistic Regression)")
    coefs = lead_model.coef_[0]
    if len(coefs) >= len(inputFeatures):
        feat_df = pd.DataFrame({'Feature': inputFeatures, 'Importance': coefs[:len(inputFeatures)]})
    else:
        feat_df = pd.DataFrame({'Feature': [f"feature_{i}" for i in range(len(coefs))], 'Importance': coefs})
    feat_df = feat_df.sort_values(by='Importance', ascending=False)

    imp_fig, imp_ax = plt.subplots(figsize=(4, 2))
    imp_ax.barh(feat_df['Feature'], feat_df['Importance'], color='orange')
    imp_ax.invert_yaxis()
    st.pyplot(imp_fig)
except Exception as ex:
    st.warning(f"Feature importance not available: {ex}")

# Filters Top Lead
st.subheader("🎯 Filter Top Leads")
min_threshold = st.slider("Minimum lead score", 0, 20, 35)
sorted_lead = final_scored_leads[final_scored_leads['Lead_Score'] >= min_threshold]
st.write(f"Showing {len(sorted_lead)} leads with score >= {min_threshold}")
st.dataframe(sorted_lead)

# Summary Statistics
st.subheader("📊 Lead Score Summary")
if 'Lead_Score' in final_scored_leads.columns:
    avg_score = final_scored_leads['Lead_Score'].mean()
    min_score = final_scored_leads['Lead_Score'].min()
    max_score = final_scored_leads['Lead_Score'].max()
    st.write(f"- Average Lead Score: {avg_score:.2f}")
    st.write(f"- Minimum Lead Score: {min_score:.2f}")
    st.write(f"- Maximum Lead Score: {max_score:.2f}")

#Sorting Options
st.subheader("🔽 Sort Leads")
sorted_features = st.selectbox(
    "Sort by feature",
    options=final_scored_leads.columns.tolist(),
    index=final_scored_leads.columns.get_loc('Lead_Score') if 'Lead_Score' in final_scored_leads.columns else 0
)
ascending_order_sort = st.checkbox("Sort in ascending order", value=False)
st.dataframe(final_scored_leads.sort_values(by=sorted_features, ascending=ascending_order_sort))
