import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from get_weather_data import *
from get_electricity_prices import *
from format_data import *


def create_dir():
    os.makedirs('model', exist_ok=True)





def train_model(data):
    # Drop unnecessary columns
    data = data.drop(columns=['date', 'city'])
    X = data.drop(columns=['price_SE'])
    y = data['price_SE']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define the preprocessing steps
    numeric_features = X.columns
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('poly', PolynomialFeatures(degree=2, include_bias=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ]
    )
    
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=200,  
        learning_rate=0.1,
        max_depth=7,
        subsample=0.8,
        colsample_bytree=1.0
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Mean Squared Error: {mse}")
    print(f"R-squared: {r2}")

    pipeline.named_steps['model'].save_model('model/xgboost_best_model.json')



# def train_model(data):
#     data = data.drop(columns=['date', 'city'])
#     X = data.drop(columns=['price_SE'])
#     y = data['price_SE']

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    

#     numeric_features = X.columns
#     numeric_transformer = Pipeline(steps=[
#         ('scaler', StandardScaler()),
#         ('poly', PolynomialFeatures(degree=2, include_bias=False))
#     ])
    
#     preprocessor = ColumnTransformer(
#         transformers=[
#             ('num', numeric_transformer, numeric_features)
#         ]
#     )
    
#     model = xgb.XGBRegressor(objective='reg:squarederror')

#     pipeline = Pipeline(steps=[
#         ('preprocessor', preprocessor),
#         ('model', model)
#     ])

#     # param_grid = {
#     #     'model__n_estimators': [200, 300],
#     #     'model__learning_rate': [0.2, 0.3],
#     #     'model__max_depth': [7, 9],
#     #     'model__subsample': [0.8, 1.0],
#     #     'model__colsample_bytree': [0.8, 1.0],
#     #     'model__gamma': [0, 0.1, 0.2],
#     #     'model__min_child_weight': [1, 3],
#     #     'model__reg_alpha': [0, 0.01],
#     #     'model__reg_lambda': [1, 1.5]
#     # }

#     # grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1)
#     # grid_search.fit(X_train, y_train)

#     # best_params = grid_search.best_params_
#     # best_model = grid_search.best_estimator_

#     print(f"Best parameters: {best_params}")

#     y_pred = best_model.predict(X_test)
#     mse = mean_squared_error(y_test, y_pred)
#     r2 = r2_score(y_test, y_pred)
    
#     print(f"Mean Squared Error: {mse}")
#     print(f"R-squared: {r2}")

#     best_model.named_steps['model'].save_model('model/xgboost_best_model.json')



   

def x():
    malmox, malmoy = 55.6059, 13.0007
    goteborgx, goteborgy = 57.7089, 11.9746
    stockholmx, stockholmy = 59.3294, 18.0687
    sundsvallx, sundsvally = 62.3913, 17.3063

    ''' 
    Training model for site SE2
    Fitting 3 folds for each of 243 candidates, totalling 729 fits
    Best parameters: {'colsample_bytree': 1.0, 'learning_rate': 0.2, 'max_depth': 7, 'n_estimators': 200, 'subsample': 0.8}
    Mean Squared Error: 0.07537688601702841
    R-squared: 0.7916138326044915
    Training model for site SE3
    Fitting 3 folds for each of 243 candidates, totalling 729 fits
    Best parameters: {'colsample_bytree': 1.0, 'learning_rate': 0.2, 'max_depth': 7, 'n_estimators': 200, 'subsample': 1.0}
    Mean Squared Error: 0.11114019199904988
    R-squared: 0.8079877365823875
    Training model for site SE4
    Fitting 3 folds for each of 243 candidates, totalling 729 fits
    Best parameters: {'colsample_bytree': 1.0, 'learning_rate': 0.1, 'max_depth': 7, 'n_estimators': 200, 'subsample': 0.8}
    Mean Squared Error: 0.18177456341996337
    R-squared: 0.7256259836226012 '''



def main():
    print("Started")
    df_weather = get_historical_weather("Stockhom", "2022-11-01", "2025-01-03", 59.3294, 18.0687)
    #df_price = get_data("SE3")
    changed_weather = process_weather_data(df_weather)
    df_other = pd.read_csv('data/entose_data.csv')

    merged_data_df = merge_data(changed_weather, df_other)

    print(changed_weather.head())
    #print(df_price.head())
    print(df_other.head())

    print("----\n")
    print("----\n")
    print("----\n")
    print(merged_data_df.head())

    print("----\n")
    print("----\n")
    print("----\n")

    train_model(merged_data_df)

if __name__ == "__main__":
    main()