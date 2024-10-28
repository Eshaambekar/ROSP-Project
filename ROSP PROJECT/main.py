from flask import Flask, render_template, request
import pandas as pd
import yfinance as yf
from textblob import TextBlob

app = Flask(__name__)

# Load the dataset of tweets (Assuming the dataset has 'Tweet' and 'Stock Name' columns)
tweets_df = pd.read_csv('stock_tweets.csv')  # Replace with your dataset path

# Analyze sentiment
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    return analysis.sentiment.polarity

# Add sentiment polarity to the DataFrame
tweets_df['polarity'] = tweets_df['Tweet'].apply(analyze_sentiment)

# Get unique stock names
stock_names = tweets_df['Stock Name'].unique()

# Function to fetch stock data
def fetch_stock_data(stock_name, interval):
    d = yf.download(stock_name, interval=interval, period='1mo')
    return d

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    stock_name = request.form.get('stock_name', stock_names[0])  # Default to first stock
    interval = request.form.get('interval', '1d')  # Default to 1 day

    stock_data = fetch_stock_data(stock_name, interval)

    # Calculate average sentiment for the selected stock
    avg_sentiment = tweets_df[tweets_df['Stock Name'] == stock_name]['polarity'].mean()
    decision = make_decision(avg_sentiment)

    # Convert the 'Date' column to string format for easier rendering in the template
    stock_data.reset_index(inplace=True)
    stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')  # Change format as needed

    return render_template('dashboard.html', stock_names=stock_names, stock_name=stock_name,
                           stock_data=stock_data, avg_sentiment=avg_sentiment, decision=decision)

def make_decision(sentiment):
    if sentiment > 0.1:
        return "Buy"
    elif sentiment < -0.1:
        return "Sell"
    else:
        return "Hold"

if __name__ == '__main__':
    app.run(debug=True)
