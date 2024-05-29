from datetime import timedelta

import plotly.graph_objs as go
import pandas as pd
from influxdb import InfluxDBClient


def get_data(query):
    # Connect to InfluxDB and fetch data
    client = InfluxDBClient(host='10.10.10.11')
    client.switch_database('ISS')
    
    results = client.query(query)
    client.close()

    return pd.DataFrame.from_records(results.get_points())


def get_data_in_chunks(thing, start_date, end_date, chunk_size_days):
    # Connect to InfluxDB
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('ISS')
    
    # Calculate the number of chunks by dividing the date range into chunk_size_days
    current_start_date = start_date

    # Initialize an empty list to store DataFrame chunks
    df_chunks = []

    while current_start_date < end_date:
        current_end_date = min(current_start_date + timedelta(days=chunk_size_days), end_date)
        
        # Formulate query for the current chunk
        query = f'SELECT * FROM \"{thing}\" WHERE time >= \'{current_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")}\' AND time < \'{current_end_date.strftime("%Y-%m-%dT%H:%M:%SZ")}\''
        # Execute query
        results = client.query(query)
        
        # Process results for the current chunk
        df_chunk = pd.DataFrame.from_records(results.get_points())
        # Here, process the dataframe, such as appending to a file, analyzing, etc.
        
        if not df_chunk.empty:
            df_chunks.append(df_chunk)

        # Prepare for the next chunk
        current_start_date = current_end_date
    
    full_df = pd.concat(df_chunks, ignore_index=True)

    client.close()

    return full_df


def plot_plotly_without_border(y_data):
    # Create Plotly trace
    trace = go.Scatter(
        y=y_data,
        mode='lines'
    )

    # Create layout without title and border
    layout = go.Layout(
        xaxis=dict(title='X-axis Label'),
        yaxis=dict(title='Y-axis Label'),
        showlegend=False,  # Disable legend
        margin=dict(t=0, b=0, l=0, r=0),  # Set margins to remove border
        paper_bgcolor='rgba(0,0,0,0)',  # Set background color to transparent
        plot_bgcolor='rgba(0,0,0,0)'  # Set plot background color to transparent
    )