import os
import logging
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import create_engine
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DB Connection (In production, load from env vars)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "transfer_analytics")
DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

def load_data_from_db():
    """Load the dbt-aggregated feature table from the database."""
    logger.info("Connecting to database to fetch training data...")
    try:
        engine = create_engine(DB_URI)
        # Using the finalized dbt model table which contains our engineered features
        query = "SELECT * FROM public.fct_player_market_features;"
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} records.")
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        # Return a dummy dataframe for testing if DB is not available
        logger.info("Returning dummy data for scaffolding purposes.")
        return pd.DataFrame({
            'age': [21, 25, 29, 31, 23],
            'goals_scored': [10, 15, 20, 5, 8],
            'assists': [5, 10, 5, 2, 6],
            'minutes_played': [2000, 2500, 3000, 1000, 1800],
            'market_value_eur': [50000000, 80000000, 60000000, 20000000, 45000000]
        })

def train_model(df):
    """Train the XGBoost regressor model."""
    logger.info("Preparing data for training...")
    
    # Target variable
    target_col = 'market_value_eur'
    
    # Feature columns (excluding target and IDs)
    features = [col for col in df.columns if col not in [target_col, 'player_id', 'player_name', 'team_id']]
    
    X = df[features]
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info("Training XGBoost Regressor...")
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    
    logger.info(f"Model Evaluation -> MAE: €{mae:,.2f} | RMSE: €{rmse:,.2f}")
    
    return model

def save_model(model, filename="model.pkl"):
    """Save the model to disk for CI/CD baking."""
    # This file will be picked up by the Dockerfile during the CI/CD build
    joblib.dump(model, filename)
    logger.info(f"Model saved to {filename}")

def main():
    df = load_data_from_db()
    
    if df is not None and not df.empty:
        model = train_model(df)
        save_model(model, filename="model.pkl")
    else:
        logger.error("No data available for training.")

if __name__ == "__main__":
    main()
