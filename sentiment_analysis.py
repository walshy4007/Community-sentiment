from nltk.sentiment import SentimentIntensityAnalyzer
from database import fetch_sentiment_data

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(content):
    return sia.polarity_scores(content)

def generate_sentiment_report(ctx, query, params):
    results = fetch_sentiment_data(query, params)
    if not results:
        return "No data to report."

    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    total_messages = sum(count for _, count in results)
    for sentiment, count in results:
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += count

    if total_messages > 0:
        report_parts = []
        if ctx.channel:
            report_parts.append(f"Channel <#{ctx.channel.id}>")
        if hasattr(ctx, 'days'):
            report_parts.append(f"for the past {ctx.days} days")
        report_type = " and ".join(report_parts) if report_parts else "Server-wide"
        report = (
            f"{report_type} Sentiment Report:\n"
            f"\n"
            f"Number of messages used for analysis: {total_messages}\n"
            f"- Positive: {sentiment_counts['positive'] / total_messages:.2%}\n"
            f"- Neutral: {sentiment_counts['neutral'] / total_messages:.2%}\n"
            f"- Negative: {sentiment_counts['negative'] / total_messages:.2%}\n"
        )
    else:
        report = "No data to report."
    return report
