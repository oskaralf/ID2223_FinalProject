import pandas as pd
import xgboost as xgb

def load_model(model_path):
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    return model

def predict_prices(model, data):
    data = data.drop(columns=['date', 'time_start', 'city'])
    X = data.drop(columns=['price'])
    predictions = model.predict(X)
    return predictions

def main():
    model = load_model('model/xgboost_model_SE4.json')
    new_data = pd.read_csv('data/new_data.csv')
    predictions = predict_prices(model, new_data)

if __name__ == "__main__":
    main()

    