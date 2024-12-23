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

def merge_data(price_df, weather_df):
    merged_df = pd.merge(price_df, weather_df, on=['time_start'])
    return merged_df

def main():
    format_price_data('price_data_SE4.csv', 'formatted_price_data_SE4.csv')
    merge_data('formatted_price_data_SE4.csv', 'formatted_weather_data_SE4.csv', 'merged_data_SE4.csv')

if __name__ == "__main__":
    main()