import requests
import datetime
import pandas as pd
import json

def format_weather_data(weather_file, output_file):
    weather_df = pd.read_csv(weather_file)
    weather_df['time_start'] = weather_df.apply(lambda row: f"{row['date']}T{row['hour']:02d}:00:00", axis=1)
    columns_order = ['date', 'time_start'] + [col for col in weather_df.columns if col not in ['date', 'time_start']]
    weather_df = weather_df[columns_order]
    weather_df.to_csv(output_file, index=False)

def format_price_data(price_file, output_file):
    price_df = pd.read_csv(price_file)
    price_df['time_start'] = price_df['time_start'].apply(lambda x: x[:19])
    price_df.to_csv(output_file, index=False)

def merge_data(price_file, weather_file, output_file):
    price_df = pd.read_csv(price_file)
    weather_df = pd.read_csv(weather_file)
    merged_df = pd.merge(price_df, weather_df, on=['time_start'])
    merged_df.to_csv(output_file, index=False)

def main():
    format_price_data('price_data_SE4.csv', 'formatted_price_data_SE4.csv')
    merge_data('formatted_price_data_SE4.csv', 'formatted_weather_data_SE4.csv', 'merged_data_SE4.csv')

if __name__ == "__main__":
    main()