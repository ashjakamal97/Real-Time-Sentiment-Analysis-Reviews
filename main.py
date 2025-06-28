import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
from scraper import scraper
from sentiment import sentiment

# NLTK Import with error handling
try:
    nltk.download('stopwords')
except ImportError:
    st.error("NLTK library not found. Please install it by running: `pip install nltk`")
    st.stop()
except Exception as e:
    st.error(f"Error initializing NLTK: {e}")
    st.stop()

# Set page config
st.set_page_config(layout="wide", page_title="Review Analysis Dashboard")

# Title
st.title("Product Review Analysis Dashboard")

with st.form("input_form"):
    product_url = st.text_input("Enter the product URL to scrape reviews:", placeholder="https://www.example.com/product-reviews")
    pages = st.number_input("Enter the number of pages of reviews to analyze:", min_value=1, max_value=1000, value=100)
    submitted = st.form_submit_button("Submit")

if not submitted:
    st.stop()

def get_scraping_output(pages, product_url):
    return scraper(pages, product_url)

scraping_output, total_review_pages = get_scraping_output(pages, product_url)
st.success(f"**{len(scraping_output)} reviews fetched.**")
st.write(f"Scraping completed. Data is ready for analysis.\n Total review pages available: {total_review_pages}")
st.dataframe(scraping_output)

@st.cache_data  
def get_sentiment_output(scraping_output):
    # Assuming sentiment_analysis function processes the DataFrame and returns it
    return sentiment(scraping_output)

df = get_sentiment_output(scraping_output)

# 1. Top Words in Positive/Negative Reviews
def top_words(reviews, n=10):
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    all_words = ' '.join(reviews.dropna()).split()
    filtered_words = [w for w in all_words if w.lower() not in stop_words]
    return Counter(filtered_words).most_common(n)

st.header("1. Most Frequent Words by Sentiment")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Words in Positive Reviews")
    pos_words = top_words(df[df['Sentiment'] == 'Positive']['cleaned reviews'])
    fig, ax = plt.subplots()
    sns.barplot(y=[w[0] for w in pos_words], x=[w[1] for w in pos_words], ax=ax, palette='Greens_d')
    ax.set_title('Top Words in Positive Reviews')
    ax.set_xlabel('Frequency')
    st.pyplot(fig)

with col2:
    st.subheader("Top Words in Negative Reviews")
    neg_words = top_words(df[df['Sentiment'] == 'Negative']['cleaned reviews'])
    fig, ax = plt.subplots()
    sns.barplot(y=[w[0] for w in neg_words], x=[w[1] for w in neg_words], ax=ax, palette='Reds_d')
    ax.set_title('Top Words in Negative Reviews')
    ax.set_xlabel('Frequency')
    st.pyplot(fig)


# Download NLTK stopwords (only needed once)
nltk.download('stopwords')

# Set page config
st.set_page_config(layout="wide", page_title="Review Analysis Dashboard")

# Title
st.title("Product Review Analysis Dashboard")

# Load your data (replace with your actual data loading)
# df = pd.read_csv('your_data.csv')




# 2. Sentiment Distribution by Product
st.header("2. Sentiment Distribution by Product")
sentiment_product = pd.crosstab(df['Product'], df['Sentiment'])
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(sentiment_product, annot=True, cmap='YlGnBu', fmt='g', ax=ax)
ax.set_title('Sentiment Distribution by Product')
ax.set_ylabel('Product')
ax.set_xlabel('Sentiment')
st.pyplot(fig)

# 3. Rating Distribution
st.header("3. Overall Rating Distribution")
fig, ax = plt.subplots(figsize=(8, 6))
sns.histplot(df['Rating'], kde=True, bins=10, color='teal', ax=ax)
ax.set_title('Overall Rating Distribution')
ax.set_xlabel('Rating')
ax.set_ylabel('Count')
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# 4. Word Cloud
st.header("4. Most Common Words in Reviews")
words = ' '.join(df['cleaned reviews'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(words)
fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
ax.set_title('Most Common Words in Reviews')
st.pyplot(fig)

# 5. Compound Sentiment Score Distribution
st.header("5. Sentiment Score Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
for sentiment in df['Sentiment'].unique():
    subset = df[df['Sentiment'] == sentiment]
    sns.kdeplot(subset['Compound Score'], label=sentiment, fill=True, ax=ax)

ax.set_title('Compound Sentiment Score Distribution by Sentiment')
ax.set_xlabel('Compound Score')
ax.legend(title='Sentiment')
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# 6. Sentiment Proportions
st.header("6. Sentiment Proportions")
col1, col2 = st.columns(2)

with col1:
    sentiment_counts = df['Sentiment'].value_counts()
    colors = ['#6A5ACD', '#48D1CC', '#FF6F61']
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
           colors=colors, startangle=140)
    ax.set_title('Sentiment Proportions')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(data=df, x='Sentiment', palette='pastel', ax=ax)
    ax.set_title('Sentiment Distribution', fontsize=16)
    ax.set_xlabel('Sentiment Category')
    ax.set_ylabel('Number of Reviews')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

# 7. Sentiment Trends Over Time
st.header("7. Sentiment Trends Over Time")
df['date_review'] = pd.to_datetime(df['date_review'], errors='coerce')
time_sentiment = df.groupby([df['date_review'].dt.to_period('M'), 'Sentiment']).size().unstack().fillna(0)

fig, ax = plt.subplots(figsize=(10, 6))
time_sentiment.plot(kind='line', marker='o', ax=ax)
ax.set_title('Sentiment Trends Over Time')
ax.set_xlabel('Review Month')
ax.set_ylabel('Number of Reviews')
ax.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
st.pyplot(fig)