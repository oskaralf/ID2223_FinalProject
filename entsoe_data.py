
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
    country_code = 'SE_3' 

    # Neighboring countries and their codes
    neighboring_countries = {
        "finland": "FI",
        "norway": "10YNO-1--------2",
        "denmark": "10YDK-1--------W",
    }

    try:
        data_frames = []
        try:
            actual_load = ensure_valid_series(
                client.query_load(country_code, start=start_date, end=end_date),
                "load_SE3",
                start_date,
                end_date
            )
            data_frames.append(actual_load.rename(columns={actual_load.columns[0]: "load_se3"}))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical load for SE3: {e}")

        for country_name, country_code in neighboring_countries.items():
            try:
                load = ensure_valid_series(
                    client.query_load(country_code, start=start_date, end=end_date),
                    f"load_{country_name}",
                    start_date,
                    end_date
                )
                data_frames.append(load.rename(columns={load.columns[0]: f"load_{country_name}"}))
                print(f"[DEBUG] Successfully fetched load data for {country_name}.")
            except Exception as e:
                print(f"[DEBUG] Error fetching historical load for {country_name}: {e}")

        try:
            day_ahead_prices = ensure_valid_series(
                client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
                "prices",
                start_date,
                end_date
            )
            data_frames.append(day_ahead_prices.to_frame(name="prices"))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical day-ahead prices: {e}")

        try:
            total_generation = ensure_valid_series(
                client.query_generation(country_code, start=start_date, end=end_date),
                "total_generation",
                start_date,
                end_date
            )
            data_frames.append(total_generation.add_prefix("total_generation_"))
        except Exception as e:
            print(f"[DEBUG] Error fetching historical total generation: {e}")

        for country_name, country_code in neighboring_countries.items():
            # Export: SE3 -> Country
            try:
                export_flows = client.query_crossborder_flows("SE_3", country_code, start=start_date, end=end_date)
                if export_flows is not None and not export_flows.empty:
                    export_flows.index = pd.to_datetime(export_flows.index)
                    export_flows = export_flows.resample("h").mean()
                    data_frames.append(
                        export_flows.to_frame(name=f"flows_se3_to_{country_name}")
                    )
                    print(f"[DEBUG] Successfully fetched cross-border flows SE3 to {country_name}.")
                else:
                    print(f"[DEBUG] Cross-border flows SE3 to {country_name}: No data available for the given period.")
                    index = pd.date_range(start=start_date, end=end_date, freq="h", tz="Europe/Berlin")
                    empty_series = pd.Series(
                        index=index, dtype=float, name=f"flows_se3_to_{country_name}"
                    )
                    data_frames.append(empty_series.to_frame())
            except Exception as e:
                print(f"[DEBUG] Error fetching cross-border physical flows from SE3 to {country_name}: {e}")
                index = pd.date_range(start=start_date, end=end_date, freq="h", tz="Europe/Berlin")
                empty_series = pd.Series(
                    index=index, dtype=float, name=f"flows_se3_to_{country_name}"
                )
                data_frames.append(empty_series.to_frame())

            # Import: Country -> SE3
            try:
                import_flows = client.query_crossborder_flows(country_code, "SE_3", start=start_date, end=end_date)
                if import_flows is not None and not import_flows.empty:
                    import_flows.index = pd.to_datetime(import_flows.index)
                    import_flows = import_flows.resample("h").mean()
                    data_frames.append(
                        import_flows.to_frame(name=f"flows_{country_name}_to_se3")
                    )
                    print(f"[DEBUG] Successfully fetched cross-border flows {country_name} to SE3.")
                else:
                    print(f"[DEBUG] Cross-border flows {country_name} to SE3: No data available for the given period.")
                    index = pd.date_range(start=start_date, end=end_date, freq="h", tz="Europe/Berlin")
                    empty_series = pd.Series(
                        index=index, dtype=float, name=f"flows_{country_name}_to_se3"
                    )
                    data_frames.append(empty_series.to_frame())
            except Exception as e:
                print(f"[DEBUG] Error fetching cross-border physical flows from {country_name} to SE3: {e}")
                index = pd.date_range(start=start_date, end=end_date, freq="h", tz="Europe/Berlin")
                empty_series = pd.Series(
                    index=index, dtype=float, name=f"flows_{country_name}_to_se3"
                )
                data_frames.append(empty_series.to_frame())

        historical_data = pd.concat(data_frames, axis=1)

        historical_data = historical_data.reset_index()
        historical_data['date'] = (
            historical_data['index'] + pd.Timedelta(hours=1)
        ).dt.strftime('%Y-%m-%d %H:%M:%S')
        historical_data = historical_data.set_index('index')

        return historical_data.dropna()

    except Exception as e:
        print(f"[DEBUG] Error fetching historical data: {e}")
        return None


if __name__ == "__main__":
    entsoe_api = os.getenv("ENTSOE_API")

    historical_data = fetch_historical_data(entsoe_api, "2025-01-04", "2025-01-06")
    if historical_data is not None:
        print("Historical Data:")
        print(historical_data.columns)
        print(historical_data)




