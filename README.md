# Electricity
Price prediction electricity

# Data 
Electricity price data gathered through Elprisetjustnu.se, through:
https://www.elprisetjustnu.se/elpris-api

Weather data gathered through Open Meteo API, through:
https://open-meteo.com/en/docs


Modelt trained on data from 2022-11-01 until 2024-12-18. 


# Notebook 1 - Backfill
Stores the weather data and price data into feature stores for SE4 in sweden, with the weather forecast data based on the coordinates of Luleå. 
Data from 1st Nov. 2022.

The features are 
    hourly_data["temperature_2m"]
    hourly_data["precipitation"]
    hourly_data["snow_depth"]
    hourly_data["pressure_msl"]
    hourly_data["cloud_cover"]
    hourly_data["wind_speed_10m"]
    hourly_data["wind_speed_100m"]
    hourly_data["wind_direction_10m"]
    hourly_data["wind_direction_100m"]

# Notebook 2 - Pipeline
Loads the feature groups, electricity_price_data and weather_data to insert the forecast weather data, that cna be used for daily scheduling purposes. 

# Notebook 3 - Training
Trains a XGBoost model with hourly data based on the historical data. Stores it in the model registry in Hopsworks for inference

# Notebook 4 - Inference
Loads the model from Hopsworks, extracts the weather forecast data from the feature group and predicts 7 days in advance. 


# SITE OF PREDICTIONS
https://oskaralf.github.io/electricity/notebooks/Images/predicted_electricity_price_over_time_SE4.png