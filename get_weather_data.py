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

def get_historical_weather(city, start_date, end_date, latitude, longitude):

    ''' Code from Open Meteo API '''
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "precipitation", "snow_depth", "pressure_msl", "cloud_cover", "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m"]
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_snow_depth = hourly.Variables(2).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
    hourly_wind_speed_100m = hourly.Variables(6).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_direction_100m = hourly.Variables(8).ValuesAsNumpy()

    hourly_data = {"datetime": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["snow_depth"] = hourly_snow_depth
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_direction_100m"] = hourly_wind_direction_100m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe['date'] = hourly_dataframe['datetime'].dt.date
    hourly_dataframe['hour'] = hourly_dataframe['datetime'].dt.hour
    hourly_dataframe = hourly_dataframe.drop(columns=['datetime'])
    hourly_dataframe = hourly_dataframe.dropna()
    hourly_dataframe['city'] = city
    return hourly_dataframe



def get_weather_forecast(city, start_date, end_date, latitude, longitude):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "snow_depth", "pressure_msl", "cloud_cover", "wind_speed_10m", "wind_speed_120m", "wind_direction_10m", "wind_direction_120m"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_snow_depth = hourly.Variables(2).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
    hourly_wind_speed_120m = hourly.Variables(6).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_direction_120m = hourly.Variables(8).ValuesAsNumpy()

    hourly_data = {"time_start": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["snow_depth"] = hourly_snow_depth
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_speed_100m"] = hourly_wind_speed_120m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_direction_100m"] = hourly_wind_direction_120m

    
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe['city'] = city
    hourly_dataframe['time_start'] = pd.to_datetime(hourly_dataframe['time_start']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    columns_order = [
        'time_start', 'temperature_2m', 'precipitation', 'snow_depth', 'pressure_msl',
        'cloud_cover', 'wind_speed_10m', 'wind_speed_100m', 'wind_direction_10m',
        'wind_direction_100m', 'city'
    ]
    #hourly_dataframe['date'] = hourly_dataframe['datetime'].dt.date
    #hourly_dataframe['hour'] = hourly_dataframe['datetime'].dt.hour
    #hourly_dataframe = hourly_dataframe.drop(columns=['datetime'])
    hourly_dataframe = hourly_dataframe[columns_order]
    hourly_dataframe = hourly_dataframe.dropna()
    
    return hourly_dataframe

def main():
    df = pd.read_csv("price_data_SE1.csv")
    df['date'] = pd.to_datetime(df['date'])  
    earliest = df['date'].min()  
    earliest_str = earliest.strftime('%Y-%m-%d') 
    print(f"Earliest date: {earliest_str}")

    today = datetime.date.today()  
    today_str = today.strftime('%Y-%m-%d')  
    print(f"Today's date: {today_str}")

    lat = 65.5841
    lon = 22.1547
    city = "Luleå"
    weather_df = get_historical_weather(city, earliest_str, today_str, lat, lon)
    print(weather_df.head())

    weather_df.to_csv('weather_data_SE4.csv', index=False)

if __name__ == "__main__":
    main()