import csv
from textblob import TextBlob

def analyze_sentiment(csv_file="linkedin_posts.csv"):
    # Read the CSV file and perform sentiment analysis on each post
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            content = row["Content"]
            comments = row["Comments"]

            # Sentiment analysis for content
            content_sentiment = TextBlob(content).sentiment.polarity
            # Sentiment analysis for comments
            comments_sentiment = TextBlob(comments).sentiment.polarity

            # Print the sentiment analysis result
            print(f"Post Content Sentiment: {content_sentiment}")
            print(f"Comments Sentiment: {comments_sentiment}")
            print("-" * 50)

if __name__ == "__main__":
    analyze_sentiment()  # Call the sentiment analysis function
