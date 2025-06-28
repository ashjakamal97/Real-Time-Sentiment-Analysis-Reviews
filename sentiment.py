import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def sentiment(df):
    """
    Takes a DataFrame with a 'Review' column, cleans the reviews, applies VADER sentiment analysis,
    and returns the modified DataFrame with 'cleaned reviews', 'Compound Score', and 'Sentiment' columns.
    """
    # Download necessary resources (only once is enough)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)

    def clean_review(text):
        # Removes all special characters and numericals leaving the alphabets
        text = re.sub('[^A-Za-z]+', ' ', str(text))
        # Convert all characters to lowercase
        text = text.lower()
        # Tokenize each review
        tokens = nltk.word_tokenize(text)
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        # Lemmatize each word in each review
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        # Combine the cleaned tokens back into a string
        cleaned_text = ' '.join(tokens)
        return cleaned_text

    analyzer = SentimentIntensityAnalyzer()
    def vader_sentiment_analysis(Review):
        vs = analyzer.polarity_scores(Review)
        compound = vs['compound']
        sentiment = 'Positive' if compound >= 0.5 else 'Negative' if compound < 0 else 'Neutral'
        return compound, sentiment

    df['cleaned reviews'] = df['Review'].apply(clean_review)
    df[['Compound Score', 'Sentiment']] = df['cleaned reviews'].apply(vader_sentiment_analysis).tolist()
    return df

# Example usage:
# df = sentiment(df)