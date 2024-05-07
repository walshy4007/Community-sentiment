# plotting.py
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

def generate_sentiment_plot(filename, days, guild_id):
    conn = sqlite3.connect('sentiments.db')
    # Calculate the date from 'days' days ago
    start_date = datetime.now() - timedelta(days=days)
    
    # Adjust the query to filter data from 'days' days ago to now and by guild ID
    query = "SELECT timestamp, sentiment FROM sentiment_data WHERE timestamp >= ? AND guild_id = ?"
    df = pd.read_sql_query(query, conn, params=(start_date, guild_id))

    if df.empty:
        print("No data available for the specified range or guild.")
        return False

    # Ensure 'timestamp' is a datetime type and set as index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Resample and count each sentiment per day
    resampled_data = df.groupby('sentiment').resample('D').size().unstack(0).fillna(0)

    # Plotting
    plt.figure(figsize=(10, 5))
    resampled_data.plot(kind='bar', stacked=True)
    plt.title(f'Sentiment Analysis for the Last {days} Days')
    plt.xlabel('Date')
    plt.ylabel('Messages')
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(filename)
    plt.close()
    conn.close()
    return True
