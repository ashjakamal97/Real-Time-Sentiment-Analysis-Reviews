# FILE 3 streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np

st.set_page_config(layout="wide", page_title="Flipkart Sentiment Dashboard")

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv("stream_output.csv")
        df['date_review'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Length'] = df['Review'].astype(str).apply(len)
        return df
    except:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("Waiting for streamed data...")
    st.stop()

st.title("Flipkart Product Review Sentiment Dashboard")

st.subheader("Latest Reviews")
st.dataframe(df[['Product', 'Author', 'Date', 'Review', 'Sentiment']].tail(10))

# Word Cloud
st.subheader("Word Cloud")
wc = WordCloud(width=800, height=400).generate(' '.join(df['Review'].astype(str)))
fig_wc, ax_wc = plt.subplots()
ax_wc.imshow(wc, interpolation='bilinear')
ax_wc.axis('off')
st.pyplot(fig_wc)

# Sentiment Distribution
st.subheader("Sentiment Score Histogram + CDF")
fig_hist, ax_hist = plt.subplots()
ax_hist.hist(df['compound'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
sorted_scores = np.sort(df['compound'])
cdf = np.arange((1, len(sorted_scores)+1), len(sorted_scores))
ax_hist.plot(sorted_scores, cdf, color='red', linestyle='--', label='CDF')
ax_hist.set_title("Compound Score Distribution")
st.pyplot(fig_hist)

# Sentiment Over Time
st.subheader("Monthly Sentiment Trends")
df.set_index('date_review', inplace=True)
monthly = df.resample('M').agg({'compound' ['mean', 'max', 'min']})
fig_time, ax_time = plt.subplots()
monthly.plot(ax=ax_time)
st.pyplot(fig_time)
df.reset_index(inplace=True)

# Pie Chart
st.subheader("Sentiment Breakdown")
counts = df['Sentiment'].value_counts()
fig_pie, ax_pie = plt.subplots()
ax_pie.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['red','green','blue'])
st.pyplot(fig_pie)