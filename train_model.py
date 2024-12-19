import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def create_dir():
    os.makedirs('model', exist_ok=True)

def train_model():

    data = pd.read_csv('data/merged_data_SE4.csv')
    data = data.drop(columns=['date', 'city', 'time_start'])
    X = data.drop(columns=['price'])
    y = data['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Squared Error: {mse}")
    print(f"R-squared: {r2}")

    model.save_model('model/xgboost_model_SE4.json')    

def main():
    train_model()

if __name__ == "__main__":
    main()