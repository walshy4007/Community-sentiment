import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import PercentFormatter

def generate_sentiment_plots(filename_prefix, days=7, guild_id='123456789', channel_name=None, export_data=False):
    # Connect to the SQLite database and query the sentiment data
    conn = sqlite3.connect('sentiments.db')
    start_date = datetime.now() - timedelta(days=days)
    
    if channel_name:
        query = "SELECT timestamp, sentiment FROM sentiment_data WHERE timestamp >= ? AND guild_id = ? AND channel_name = ?"
        params = (start_date.strftime('%Y-%m-%d %H:%M:%S'), guild_id, channel_name)
    else:
        query = "SELECT timestamp, sentiment FROM sentiment_data WHERE timestamp >= ? AND guild_id = ?"
        params = (start_date.strftime('%Y-%m-%d %H:%M:%S'), guild_id)
    
    df = pd.read_sql_query(query, conn, params=params)

    if df.empty:
        print("No data available for the specified range or guild.")
        conn.close()
        return False, None, None

    # Convert timestamps and prepare data
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    df.set_index('timestamp', inplace=True)
    resampled_data = df.groupby('sentiment').resample('D').size().unstack(0).fillna(0)
    percentage_data = resampled_data.divide(resampled_data.sum(axis=1), axis=0)

    # Optionally export the data to CSV
    data_filename = None
    if export_data:
        data_filename = f'{filename_prefix}_data.csv'
        df.to_csv(data_filename)
        print(f"Data exported to {data_filename}")

    # Set up the plot for 100% stacked bar chart
    plt.figure(figsize=(10, 5))
    ax = percentage_data.plot(kind='bar', stacked=True)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    plt.title(f'Sentiment Analysis (Volume) for the Last {days} Days' + (f' in {channel_name}' if channel_name else ''))
    plt.xlabel('Date')
    plt.ylabel('Percentage of Messages')
    plt.ylim([0, 1])
    plt.tight_layout()
    bar_chart_filename = f'{filename_prefix}_stacked_bar.png'
    plt.savefig(bar_chart_filename)
    plt.close()

    # Set up the plot for line chart
    plt.figure(figsize=(10, 5))
    ax = percentage_data.plot(kind='line')
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    plt.title(f'Sentiment Analysis (Distribution) for the Last {days} Days' + (f' in {channel_name}' if channel_name else ''))
    plt.xlabel('Date')
    plt.ylabel('Percentage of Messages')
    plt.ylim([0, 1])
    plt.grid(True)
    plt.tight_layout()
    line_chart_filename = f'{filename_prefix}_line_chart.png'
    plt.savefig(line_chart_filename)
    plt.close()

    conn.close()
    return bar_chart_filename, line_chart_filename, data_filename