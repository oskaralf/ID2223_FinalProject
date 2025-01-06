import os
import datetime
import time
import requests
import pandas as pd
import json
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import openmeteo_requests
import requests_cache
from retry_requests import retry
import hopsworks
import hsfs
from pathlib import Path

def secrets_api(proj):
    host = "c.app.hopsworks.ai"
    api_key = os.environ.get('HOPSWORKS_API_KEY')
    conn = hopsworks.connection(host=host, project=proj, api_key_value=api_key)
    return conn.get_secrets_api()

def modify_weather_df(df):
    df.drop(['snow_depth',
       'pressure_msl', 'cloud_cover', 'wind_speed_10m',
       'wind_direction_10m', 'wind_direction_100m', 'city'], axis=1, inplace=True)
    return df

def modify_entsoe_df(df):
    # Define the columns to be merged for imported_energy
    columns_to_merge = [
        'flows_se3_to_finland', 'flows_finland_to_se3',
        'flows_se3_to_norway', 'flows_norway_to_se3',
        'flows_se3_to_denmark', 'flows_denmark_to_se3'
    ]

    df['imported_energy'] = df.apply(
        lambda row: sum(-row[col] if 'se3_to' in col else row[col] for col in columns_to_merge),
        axis=1
    )

    df = df.drop(columns=columns_to_merge)

    df['total_load'] = ( df['load_finland'] +
        df['load_norway'] + df['load_denmark'] + df['load_se3']
    )

    df = df.drop(columns=['load_finland', 'load_norway', 'load_denmark', 'load_se3'])

    columns_to_sum = [
        'total_generation_biomass', 'total_generation_fossil_gas',
        'total_generation_fossil_hard_coal', 'total_generation_fossil_oil',
        'total_generation_hydro_run_of_river_and_poundage',
        'total_generation_other_renewable', 'total_generation_solar',
        'total_generation_waste', 'total_generation_wind_offshore',
        'total_generation_wind_onshore'
    ]

    df['total_generation_se'] = df[columns_to_sum].sum(axis=1)
    df = df.drop(columns=columns_to_sum)

    return df


def create_lagging_columns(df):
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Calculate the difference in hours
    df['date_diff'] = df['date'].diff().dt.total_seconds() / 3600

 # List of original columns to avoid including newly created lagging columns
    original_columns = df.columns.tolist()

    # Loop to create lagging columns
    for column in original_columns:
        if column != 'date' and column != 'date_diff':
            df[column + '_lag'] = df[column].shift(1).where(df['date_diff'] == 1)

    # print(df.head())

    # Drop the date_diff column
    df = df.drop(columns=['date_diff'])
    print("number of rows before dropping na: ", df.shape[0])
    df = df.dropna()
    print("number of rows after dropping na: ", df.shape[0])
    # print(df.head())
    return df

def add_future_price_column(df, price_column='prices'):
    # Ensure the price column exists in the DataFrame
    if price_column not in df.columns:
        raise ValueError(f"Column '{price_column}' does not exist in the DataFrame")

    # Create the future_price column by shifting the price column backwards
    df['future_price'] = df[price_column].shift(-1)
    return df