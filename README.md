# Hourly price prediction 
This project aims to predict electricity prices in Sweden using machine learning, specifically the XGBoost algorithm. The predictions focus on the next hour's electricity price, leveraging various data points collected in real-time.

# SITE OF PREDICTIONS
https://oskaralf.github.io/electricity/notebooks/Images/predicted_electricity_price_over_time_SE4.png

## Overview of notebooks

### Notebook 1 - Backfill
Retrieves and stores the weather data and electricity data into feature stores for SE3 in Sweden, with the weather data based on the coordinates of Stockholm.

### Notebook 2 - Pipeline
Loads the feature groups, electricity_price_data and weather_data to insert the forecast weather data, that cna be used for daily scheduling purposes. 

### Notebook 3 - Training
Trains a XGBoost model with hourly data based on the historical data. Stores it in the model registry in Hopsworks for inference.

### Notebook 4 - Inference
Loads the model from Hopsworks, extracts the weather forecast data from the feature group and predicts 7 days in advance. 

## Data 

### API's used
Weather data gathered through Open Meteo API, for Stockholm cordinates, through:
https://open-meteo.com/en/docs

Electricity data gathered through Entsoe [add link]:

Model trained on data from 2022-11-01 until 2024-12-31. 

### Data collected (and brief logic on why)

#### Weather for Stockholm
Temperature: Colder weather increases heating demand, affecting electricity usage.

Rain: Impacts hydropower generation, a key energy source in Sweden.

Wind: Drives wind power generation, influencing electricity supply.

#### Entsoe electricity data

International Load: The electricity demand in neighboring countries, reported at an hourly resolution. This data reflects cross-border influences on electricity pricing.  

Swedish Load: The total electricity consumption within Sweden, collected on an hourly basis, serving as a direct indicator of domestic demand.

Cross-border flows to neighboring countries: Hourly measurements of electricity imported/exported into/from Sweden from/to neighboring countries, mirroring market dynamics and price. 20

Electricity Price: Historical hourly electricity prices in Sweden

## Method

### Feature engineering

The raw data points are processed and merged into meaningful features to train the XGBoost model. Key steps include:

Future Price Column: To predict the next hour's electricity price, a future price column is created by shifting all electricity prices forward by one hour. This ensures that the model learns to map current conditions to the next hour's price.

Imported electricity: Import and export electricity flows are combined into a single feature, "Imported Electricity." Imports are represented as positive values, while exports are represented as negative values. This approach captures the net effect of cross-border electricity trade on price fluctuations.

Total generation: All sources of manufactured electricity are aggregated into a single feature. This simplifies the representation of domestic electricity generation.

Total load: The total electricity load across the Nordic countries is calculated and combined into a single feature. This accounts for the regional demand that should be influencing Sweden's electricity market.

Lag Features: Creating features based on the current and previous hour's values for all features (including weather). These lagged values provide temporal context. 

### Hyperparameters

### Modelling and validation

### Feature importance analysis

# Results

# Further improvements

# How to run the code