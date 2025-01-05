# import os
# import pandas as pd
# from entsoe import EntsoePandasClient
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# load_dotenv()

# def ensure_valid_series(series, name, start, end):
#     """Ensure series is valid, or create an empty one if not."""
#     if series is None or series.empty:
#         print(f"[DEBUG] Data missing for {name}. Creating empty Series.")
#         index = pd.date_range(start=start, end=end, freq="h", tz="Europe/Berlin")
#         return pd.DataFrame(index=index, columns=[name], dtype=float)

#     if isinstance(series, pd.Series):
#         series.index = pd.to_datetime(series.index)
#         series.name = name
#         return series.resample("h").mean()
#     elif isinstance(series, pd.DataFrame):
#         series.index = pd.to_datetime(series.index)
#         return series.resample("h").mean()
#     else:
#         raise ValueError(f"Unsupported data type for {name}")

# def fetch_historical_data(api_key, start_date, end_date):
#     """Fetch historical data."""
#     client = EntsoePandasClient(api_key=api_key)

#     start_date = pd.Timestamp(start_date, tz='Europe/Berlin')
#     end_date = pd.Timestamp(end_date, tz='Europe/Berlin')
#     country_code = 'SE_3'  # Sweden bidding zone

#     try:
#         # Initialize a list to hold all DataFrames
#         data_frames = []

#         # Fetch historical load
#         try:
#             actual_load = ensure_valid_series(
#                 client.query_load(country_code, start=start_date, end=end_date),
#                 "historical_load",
#                 start_date,
#                 end_date
#             )
#             data_frames.append(actual_load.rename(columns={actual_load.columns[0]: "historical_load"}))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching historical load: {e}")

#         # Fetch historical day-ahead prices
#         try:
#             day_ahead_prices = ensure_valid_series(
#                 client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
#                 "historical_day_ahead_prices",
#                 start_date,
#                 end_date
#             )
#             data_frames.append(day_ahead_prices.to_frame(name="historical_day_ahead_prices"))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching historical day-ahead prices: {e}")

#         # Fetch historical total generation
#         try:
#             total_generation = ensure_valid_series(
#                 client.query_generation(country_code, start=start_date, end=end_date),
#                 "historical_total_generation",
#                 start_date,
#                 end_date
#             )
#             data_frames.append(total_generation.add_prefix("historical_total_generation_"))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching historical total generation: {e}")

#         # Combine historical data
#         historical_data = pd.concat(data_frames, axis=1)
#         return historical_data.ffill().dropna()

#     except Exception as e:
#         print(f"[DEBUG] Error fetching historical data: {e}")
#         return None

# def fetch_forecasted_data(api_key, start_date, end_date):
#     """Fetch forecasted data."""
#     client = EntsoePandasClient(api_key=api_key)

#     start_date = pd.Timestamp(start_date, tz='Europe/Berlin')
#     end_date = pd.Timestamp(end_date, tz='Europe/Berlin')
#     country_code = 'SE_3'  # Sweden bidding zone

#     try:
#         # Initialize a list to hold all DataFrames
#         data_frames = []

#         # Fetch forecasted load
#         try:
#             forecasted_load = ensure_valid_series(
#                 client.query_load_forecast(country_code, start=start_date, end=end_date),
#                 "forecasted_load",
#                 start_date,
#                 end_date
#             )
#             data_frames.append(forecasted_load.rename(columns={forecasted_load.columns[0]: "forecasted_load"}))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching forecasted load: {e}")

#         # Fetch forecasted day-ahead prices
#         try:
#             day_ahead_prices = ensure_valid_series(
#                 client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
#                 "forecasted_day_ahead_prices",
#                 start_date,
#                 end_date
#             )
#             data_frames.append(day_ahead_prices.to_frame(name="forecasted_day_ahead_prices"))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching forecasted day-ahead prices: {e}")

#         # Fetch forecasted wind and solar generation
#         try:
#             wind_solar_forecast = client.query_wind_and_solar_forecast(country_code, start=start_date, end=end_date)
#             wind_solar_forecast = ensure_valid_series(
#                 wind_solar_forecast, "forecasted_wind_solar_generation", start_date, end_date
#             )
#             data_frames.append(wind_solar_forecast.add_prefix("forecasted_"))
#         except Exception as e:
#             print(f"[DEBUG] Error fetching wind/solar forecast: {e}")

#         # Combine forecasted data
#         forecasted_data = pd.concat(data_frames, axis=1)
#         return forecasted_data.ffill().dropna()

#     except Exception as e:
#         print(f"[DEBUG] Error fetching forecasted data: {e}")
#         return None

# if __name__ == "__main__":
#     entsoe_api = os.getenv("ENTSOE_API")

#     # Fetch historical data
#     historical_data = fetch_historical_data(entsoe_api, "2024-01-01", "2024-12-31")
#     if historical_data is not None:
#         print("Historical Data:")
#         print(historical_data.columns)
#         print(historical_data)

#     # Fetch forecasted data
#     forecasted_data = fetch_forecasted_data(entsoe_api, "2025-01-04", "2025-01-09")
#     if forecasted_data is not None:
#         print("Forecasted Data:")

#         print(forecasted_data.columns)

#         print("--------\n")
#         print(forecasted_data.tail(50))
#         print("--------\n")
#         print(forecasted_data)


import os
import pandas as pd
from entsoe import EntsoePandasClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def ensure_valid_series(series, name, start, end):
    """Ensure series is valid, or create an empty one if not."""
    if series is None or series.empty:
        print(f"[DEBUG] Data missing for {name}. Creating empty Series.")
        index = pd.date_range(start=start, end=end, freq="h", tz="Europe/Berlin")
        return pd.DataFrame(index=index, columns=[name], dtype=float)

    if isinstance(series, pd.Series):
        series.index = pd.to_datetime(series.index)
        series.name = name
        return series.resample("h").mean()
    elif isinstance(series, pd.DataFrame):
        series.index = pd.to_datetime(series.index)
        return series.resample("h").mean()
    else:
        raise ValueError(f"Unsupported data type for {name}")

def fetch_historical_data(api_key, start_date, end_date):
    """Fetch historical data."""
    client = EntsoePandasClient(api_key=api_key)

    start_date = pd.Timestamp(start_date, tz='Europe/Berlin')
    end_date = pd.Timestamp(end_date, tz='Europe/Berlin')
    country_code = 'SE_3'  # Sweden bidding zone

    # Neighboring countries and their codes
    neighboring_countries = {
        "Finland": "FI",
        "Norway": "10YNO-1--------2",
        "Denmark": "10YDK-1--------W",
    }

    try:
        # Initialize a list to hold all DataFrames
        data_frames = []

        # Fetch historical load
        try:
            actual_load = ensure_valid_series(
                client.query_load(country_code, start=start_date, end=end_date),
                "historical_load",
                start_date,
                end_date
            )
            data_frames.append(actual_load.rename(columns={actual_load.columns[0]: "historical_load"}))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical load: {e}")

        # Fetch historical day-ahead prices
        try:
            day_ahead_prices = ensure_valid_series(
                client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
                "historical_day_ahead_prices",
                start_date,
                end_date
            )
            data_frames.append(day_ahead_prices.to_frame(name="historical_day_ahead_prices"))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical day-ahead prices: {e}")

        # Fetch historical total generation
        try:
            total_generation = ensure_valid_series(
                client.query_generation(country_code, start=start_date, end=end_date),
                "historical_total_generation",
                start_date,
                end_date
            )
            data_frames.append(total_generation.add_prefix("historical_total_generation_"))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical total generation: {e}")

        # Fetch historical loads for neighboring countries
        for country_name, country_code in neighboring_countries.items():
            try:
                load = ensure_valid_series(
                    client.query_load(country_code, start=start_date, end=end_date),
                    f"historical_load_{country_name}",
                    start_date,
                    end_date
                )
                data_frames.append(load.rename(columns={load.columns[0]: f"historical_load_{country_name}"}))
            except Exception as e:
                print(f"[DEBUG] Error fetching historical load for {country_name}: {e}")

        # Combine historical data
        historical_data = pd.concat(data_frames, axis=1)
        return historical_data.ffill().dropna()

    except Exception as e:
        print(f"[DEBUG] Error fetching historical data: {e}")
        return None

def fetch_forecasted_data(api_key, start_date, end_date):
    """Fetch forecasted data."""
    client = EntsoePandasClient(api_key=api_key)

    start_date = pd.Timestamp(start_date, tz='Europe/Berlin')
    end_date = pd.Timestamp(end_date, tz='Europe/Berlin')
    country_code = 'SE_3'  # Sweden bidding zone

    # Neighboring countries and their codes
    neighboring_countries = {
        "Finland": "FI",
        "Norway": "10YNO-1--------2",
        "Denmark": "10YDK-1--------W",
    }

    try:
        # Initialize a list to hold all DataFrames
        data_frames = []

        # Fetch forecasted load
        try:
            forecasted_load = ensure_valid_series(
                client.query_load_forecast(country_code, start=start_date, end=end_date),
                "forecasted_load",
                start_date,
                end_date
            )
            data_frames.append(forecasted_load.rename(columns={forecasted_load.columns[0]: "forecasted_load"}))
        except Exception as e:
            print(f"[DEBUG] Error fetching forecasted load: {e}")

        # Fetch forecasted day-ahead prices
        try:
            day_ahead_prices = ensure_valid_series(
                client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
                "forecasted_day_ahead_prices",
                start_date,
                end_date
            )
            data_frames.append(day_ahead_prices.to_frame(name="forecasted_day_ahead_prices"))
        except Exception as e:
            print(f"[DEBUG] Error fetching forecasted day-ahead prices: {e}")

        # Fetch forecasted wind and solar generation
        try:
            wind_solar_forecast = client.query_wind_and_solar_forecast(country_code, start=start_date, end=end_date)
            wind_solar_forecast = ensure_valid_series(
                wind_solar_forecast, "forecasted_wind_solar_generation", start_date, end_date
            )
            data_frames.append(wind_solar_forecast.add_prefix("forecasted_"))
        except Exception as e:
            print(f"[DEBUG] Error fetching wind/solar forecast: {e}")

        # Fetch forecasted loads for neighboring countries
        for country_name, country_code in neighboring_countries.items():
            try:
                load_forecast = ensure_valid_series(
                    client.query_load_forecast(country_code, start=start_date, end=end_date),
                    f"forecasted_load_{country_name}",
                    start_date,
                    end_date
                )
                data_frames.append(load_forecast.rename(columns={load_forecast.columns[0]: f"forecasted_load_{country_name}"}))
            except Exception as e:
                print(f"[DEBUG] Error fetching forecasted load for {country_name}: {e}")

        # Combine forecasted data
        forecasted_data = pd.concat(data_frames, axis=1)
        return forecasted_data.ffill().dropna()

    except Exception as e:
        print(f"[DEBUG] Error fetching forecasted data: {e}")
        return None

if __name__ == "__main__":
    entsoe_api = os.getenv("ENTSOE_API")

    # Fetch historical data
    historical_data = fetch_historical_data(entsoe_api, "2024-01-01", "2024-12-31")
    historical_data = historical_data.drop(columns=['historical_total_generation_Fossil Gas', 'historical_total_generation_Hydro Water Reservoir', 'historical_total_generation_Nuclear',  'historical_total_generation_Other'])
    if historical_data is not None:
        print("Historical Data:")
        print(historical_data.columns)
        print(historical_data)

    # Fetch forecasted data
    forecasted_data = fetch_forecasted_data(entsoe_api, "2025-01-04", "2025-01-09")
    if forecasted_data is not None:
        print("Forecasted Data:")

        print(forecasted_data.columns)

        print("--------\n")
        print(forecasted_data.tail(50))
        print("--------\n")
        print(forecasted_data)
