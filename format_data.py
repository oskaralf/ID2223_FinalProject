import requests
import datetime
import pandas as pd
import json

def format_weather_data(weather_df):
    # Combine 'date' and 'hour' into 'time_start' in the desired format
    weather_df['time_start'] = weather_df.apply(lambda row: f"{row['date']}T{row['hour']:02d}:00:00", axis=1)
    weather_df = weather_df.drop(columns=['date', 'hour'])
    columns_order = ['time_start'] + [col for col in weather_df.columns if col != 'time_start']
    weather_df = weather_df[columns_order]
    weather_df['time_start'] = pd.to_datetime(weather_df['time_start'], errors='coerce')
    
    if weather_df['time_start'].isnull().any():
        raise ValueError("Some 'time_start' values could not be converted to datetime.")
    
    weather_df['time_start'] = weather_df['time_start'].dt.tz_localize(None)

    weather_df['time_start'] = weather_df['time_start'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    return weather_df

def format_price_data(price_file, output_file):
    price_df = pd.read_csv(price_file)
    price_df['time_start'] = price_df['time_start'].apply(lambda x: x[:19])
    return price_df

def process_price_data(input_file, output_file):

    df = pd.read_csv(input_file)
    df['time_start'] = pd.to_datetime(df['time_start'], errors='coerce', utc=True)
    if df['time_start'].isnull().any():
        raise ValueError("Some 'time_start' values could not be converted to datetime.")
    df['time_start'] = df['time_start'].dt.tz_convert(None)
    df['time_start'] = df['time_start'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df.to_csv(output_file, index=False)


def merge_weather_and_price_data(weather_file, price_file, output_file):
    # Read the weather and price data from CSV files
    weather_df = pd.read_csv(weather_file)
    price_df = pd.read_csv(price_file)
    
    # Convert 'time_start' to datetime to ensure proper merging
    weather_df['time_start'] = pd.to_datetime(weather_df['time_start'], errors='coerce')
    price_df['time_start'] = pd.to_datetime(price_df['time_start'], errors='coerce')
    
    # Check for any conversion issues
    if weather_df['time_start'].isnull().any() or price_df['time_start'].isnull().any():
        raise ValueError("Some 'time_start' values could not be converted to datetime.")
    
    # Format 'time_start' to the desired format
    weather_df['time_start'] = weather_df['time_start'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    price_df['time_start'] = price_df['time_start'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Merge the DataFrames based on the 'time_start' column
    merged_df = pd.merge(weather_df, price_df, on='time_start', suffixes=('_weather', '_price'))
    
    # Ensure the columns are in the desired order
    columns_order = [
        'date', 'time_start', 'price', 'temperature_2m', 'precipitation', 'snow_depth',
        'pressure_msl', 'cloud_cover', 'wind_speed_10m', 'wind_speed_100m',
        'wind_direction_10m', 'wind_direction_100m', 'city'
    ]
    merged_df = merged_df[columns_order]
    
    # Write the merged DataFrame to the output CSV file
    merged_df.to_csv(output_file, index=False)



def process_weather_data(df):

    df['date'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour'], unit='h')

    df = df.drop(columns=['hour'])
    cols = ['date'] + [col for col in df.columns if col != 'date']
    df = df[cols]
    
    return df


def merge_data(df1, df2):
    # Ensure 'date' columns are of the same datetime64[ns] type
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])
    
    # Merge the two DataFrames on the 'date' column
    merged_df = pd.merge(df1, df2, on='date', how='inner')
    return merged_df

def main():
    #format_price_data('price_data_SE1.csv', 'formatted_price_data_SE1.csv')
    pass

if __name__ == "__main__":
    main()