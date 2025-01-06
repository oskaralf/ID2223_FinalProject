import pandas as pd
import os
import numpy as np
import requests
from datetime import datetime, timedelta
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta
import time
import json
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import openmeteo_requests
import requests_cache
from retry_requests import retry
import hsfs
from pathlib import Path
from dotenv import load_dotenv
import hopsworks
import sys

root_dir = Path().resolve().parent
sys.path.append(str(root_dir))

from format_data import format_weather_data, format_price_data, process_weather_data
from get_electricity_prices import get_data
from get_weather_data import get_historical_weather, get_weather_forecast
from entsoe_data import fetch_historical_data, ensure_valid_series

if not os.getenv("CI"):
    load_dotenv()
    
hopsworks_api = os.getenv("HOPSWORKS_API_KEY")
entose_api = os.getenv("ENTSOE_API")

if not hopsworks_api:
    raise ValueError("HOPSWORKS_API_KEY is not set.")
if not entose_api:
    raise ValueError("ENTSOE_API is not set.")

os.environ["ENTSOE_API"] = entose_api
os.environ["HOPSWORKS_API_KEY"] = hopsworks_api

project = hopsworks.login()
fs = project.get_feature_store() 
print(f"Connected to project: {project.name}")

start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

forecast = get_weather_forecast("Stockholm", start_date, end_date, 59.3294, 18.0687)
formatted_forecast_df = process_weather_data(forecast)

weather_fg = fs.get_feature_group(
    name='weather_data_3',
    version=1,
)
entsoe_fg = fs.get_feature_group(
    name='entsoe_data_3',
    version=1,
)

formatted_forecast_df = formatted_forecast_df.dropna()
weather_fg.insert(formatted_forecast_df)

entsoe_df = fetch_historical_data(entose_api, start_date, end_date)
entsoe_df.columns = entsoe_df.columns.str.lower()
entsoe_df.columns = entsoe_df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
entsoe_df['date'] = pd.to_datetime(entsoe_df['date'])
entsoe_df['date'] = pd.to_datetime(entsoe_df['date']).dt.tz_localize('UTC').dt.tz_convert(None)
entsoe_df = entsoe_df.dropna()
entsoe_fg.insert(entsoe_df)