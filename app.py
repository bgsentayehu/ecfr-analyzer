# 📦 app.py — Streamlit Frontend for eCFR Analyzer

import streamlit as st
import pandas as pd
import json

# -----------------------------------
# 📥 Load word count data from backend
# -----------------------------------
try:
    with open("word_counts.json") as f:
        word_counts = json.load(f)
except FileNotFoundError:
    st.error("❌ word_counts.json not found. Please run the backend script first.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(list(word_counts.items()), columns=["Agency", "Word Count"])
df = df.sort_values("Word Count", ascending=False)

# ------------------------------
# 🎨 Streamlit Page Configuration
# ------------------------------
st.set_page_config(page_title="eCFR Analyzer", layout="wide")
st.title("📊 eCFR Analyzer")
st.subheader("Total Word Count by Federal Agency (latest issue date)")

# ------------------------------
# 🔍 Filter by Agency (optional)
# ------------------------------
agency_filter = st.selectbox("🔎 Select an agency to filter (or view all):", ["All"] + df["Agency"].tolist())

if agency_filter != "All":
    filtered_df = df[df["Agency"] == agency_filter]
else:
    filtered_df = df

# --------------------
# 📊 Bar Chart Display
# --------------------
st.subheader("📉 Word Count Bar Chart")
st.bar_chart(filtered_df.set_index("Agency"))

# ----------------
# 📋 Data Table View
# ----------------
st.subheader("🗂 Detailed Table")
st.dataframe(filtered_df, use_container_width=True)

# ------------------
# ⬇️ Download Button
# ------------------
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, "word_counts.csv", "text/csv")
