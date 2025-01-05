import os
import pandas as pd
from entsoe import EntsoePandasClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def fetch_energy_data(key, start_date, end_date):
    client = EntsoePandasClient(api_key=key)

    start_date = pd.Timestamp(start_date, tz='Europe/Berlin')
    end_date = pd.Timestamp(end_date, tz='Europe/Berlin')  
    country_code = 'SE_3'  

    def ensure_valid_series(series, name, start, end):
        if series is None or series.empty:
            print(f"Data missing for {name}. Creating empty Series.")
            index = pd.date_range(start=start, end=end, freq="h", tz="Europe/Berlin")
            return pd.Series(index=index, dtype=float, name=name)

        series.index = pd.to_datetime(series.index)
        series.name = name

        return series.resample("h").mean()

    try:
        actual_load_se = ensure_valid_series(
            client.query_load(country_code, start=start_date, end=end_date),
            "load_se",
            start_date,
            end_date
        )
        day_ahead_prices = ensure_valid_series(
            client.query_day_ahead_prices(country_code, start=start_date, end=end_date),
            "price_se",
            start_date,
            end_date
        )

        flows_se_fi = ensure_valid_series(
            client.query_crossborder_flows(country_code, "FI", start=start_date, end=end_date),
            "flows_se_finland",
            start_date,
            end_date
        )

        flows_se_no = ensure_valid_series(
            client.query_crossborder_flows(country_code, "10YNO-1--------2", start=start_date, end=end_date),
            "flows_se_norway",
            start_date,
            end_date
        )

        flows_se_dk = ensure_valid_series(
            client.query_crossborder_flows(country_code, "10YDK-1--------W", start=start_date, end=end_date),
            "flows_se_denmark",
            start_date,
            end_date
        )

        load_fi = ensure_valid_series(
            client.query_load("FI", start=start_date, end=end_date),
            "load_finland",
            start_date,
            end_date
        )

        load_no = ensure_valid_series(
            client.query_load("10YNO-1--------2", start=start_date, end=end_date),
            "load_norway",
            start_date,
            end_date
        )

        load_de = ensure_valid_series(
            client.query_load("10Y1001A1001A83F", start=start_date, end=end_date),
            "load_germany",
            start_date,
            end_date
        )

        load_dk = ensure_valid_series(
            client.query_load("10YDK-1--------W", start=start_date, end=end_date),
            "load_denmark",
            start_date,
            end_date
        )

        try:
            hydro_storage = client.query_aggregate_water_reservoirs_and_hydro_storage(country_code, start=start_date, end=end_date)
            hydro_storage = ensure_valid_series(hydro_storage, "hydro_storage_se", start_date, end_date)
        except Exception as e:
            print(f"Hydro storage data unavailable for {start_date} to {end_date}: {e}")
            print("Attempting to fetch the latest available data...")

            try:
                latest_start = pd.Timestamp.now(tz="Europe/Berlin") - pd.Timedelta(days=7)
                latest_end = pd.Timestamp.now(tz="Europe/Berlin")
                hydro_storage = client.query_aggregate_water_reservoirs_and_hydro_storage(country_code, start=latest_start, end=latest_end)
                #hydro_storage = ensure_valid_series(hydro_storage, "hydro_storage_se", latest_start, latest_end)
                print("Successfully fetched the latest available hydro storage data.")
            except Exception as fallback_error:
                print(f"Failed to fetch the latest hydro storage data: {fallback_error}")
                hydro_storage = pd.Series(dtype=float, name="hydro_storage_se")

        energy_data = pd.concat([
            actual_load_se,
            day_ahead_prices,
            flows_se_fi,
            flows_se_no,
            flows_se_dk,  
            load_fi,
            load_no,
            load_de,
            load_dk,
            hydro_storage
        ], axis=1)

        energy_data.columns = [
            "load_se", "price_se", "flows_se_finland", "flows_se_norway", "flows_se_denmark",
            "load_finland", "load_norway", "load_germany", "load_denmark", "hydro_storage_se"
        ]

        energy_data = energy_data.ffill()
        energy_data = energy_data.dropna()
        energy_data = energy_data.reset_index()
        energy_data['date'] = energy_data['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        energy_data = energy_data.drop(columns=['index'])

        return energy_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error fetching data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    entose_api = os.getenv("ENTSOE_API")
    df_energy_data = fetch_energy_data(entose_api, "2025-01-04", "2025-01-06")
    if df_energy_data is not None:
        print(df_energy_data)
    # from entsoe import EntsoePandasClient
    # import pandas as pd
    # from datetime import datetime

    # start_date = "2025-01-03"
    # end_date = "2025-01-04"

    # client = EntsoePandasClient(api_key=entose_api)
    # start_date = pd.Timestamp("2025-01-03", tz="Europe/Berlin")
    # end_date = pd.Timestamp("2025-01-04", tz="Europe/Berlin")
    # country_code = "SE_3"

    # print(hydro_storage)
