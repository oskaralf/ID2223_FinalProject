import requests
import datetime
import pandas as pd

def get_price_data(year, month, day, price_class):
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month:02d}-{day:02d}_{price_class}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def extract_hourly_prices(data):
    hourly_prices = []
    for entry in data:
        hourly_prices.append({
            'time_start': entry['time_start'],
            'SEK_per_kWh': entry['SEK_per_kWh']
        })
    return hourly_prices

def get_data(seX):
    start_date = datetime.date(2022, 11, 1)
    end_date = datetime.date.today()
    date_range = pd.date_range(start_date, end_date)

    price_data = []
    for single_date in date_range:
        year = single_date.year
        month = single_date.month
        day = single_date.day
        price_class = seX

        try:
            data = get_price_data(year, month, day, price_class)
            hourly_prices = extract_hourly_prices(data)
            for price in hourly_prices:
                price_data.append({
                    'date': single_date,
                    'time_start': price['time_start'],
                    'price': price['SEK_per_kWh']
                })
        except Exception as e:
            print(f"An error occurred for {single_date}: {e}")
    
    df = pd.DataFrame(price_data)
    

    return df

def get_todays_data(price_class):
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    
    data = get_price_data(year, month, day, price_class)
    hourly_prices = extract_hourly_prices(data)
    price_data = []
    for price in hourly_prices:
        price_data.append({
            'date': today,
            'time_start': price['time_start'],
            'price': price['SEK_per_kWh']
        })
    
    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    return df



def main():
    df = get_data('SE3')
    print(df)

if __name__ == "__main__":
    main()