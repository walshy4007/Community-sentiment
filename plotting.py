import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

def generate_sentiment_plot(filename='sentiment_plot.png', days=7, guild_id='123456789', export_data=False):
    # Connect to the SQLite database and query the sentiment data
    conn = sqlite3.connect('sentiments.db')
    start_date = datetime.now() - timedelta(days=days)
    query = "SELECT timestamp, sentiment FROM sentiment_data WHERE timestamp >= ? AND guild_id = ?"
    df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d %H:%M:%S'), guild_id))

    if df.empty:
        print("No data available for the specified range or guild.")
        conn.close()
        return False

    # Ensure the timestamp format can handle microseconds and convert to a DateTime object
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')

    # Resample the data by grouping by sentiment and date, filling missing values with 0
    df.set_index('timestamp', inplace=True)
    resampled_data = df.groupby('sentiment').resample('D').size().unstack(0).fillna(0)

    # Plotting the line graph
    plt.figure(figsize=(10, 5))
    resampled_data.plot(kind='line')
    plt.title(f'Sentiment Analysis for the Last {days} Days')
    plt.xlabel('Date')
    plt.ylabel('Messages')
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(filename)
    plt.close()

    # Optionally export the data to CSV
    if export_data:
        data_filename = f'sentiment_data_{guild_id}_{days}d.csv'
        resampled_data.to_csv(data_filename)
        print(f"Data exported to {data_filename}")

    conn.close()
    return True
