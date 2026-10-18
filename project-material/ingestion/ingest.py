import os
import json
import logging
import requests
import pandas as pd
import boto3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_KEY = os.getenv("API_FOOTBALL_KEY", "dummy_key")
API_HOST = "v3.football.api-sports.io"
BASE_URL = f"https://{API_HOST}"
S3_BUCKET = os.getenv("S3_STAGING_BUCKET", "football-analytics-staging-bucket")

# Top 5 European Leagues (IDs for API-Football)
# 39: Premier League, 140: La Liga, 135: Serie A, 78: Bundesliga, 61: Ligue 1
LEAGUES = [39, 140, 135, 78, 61]
CURRENT_SEASON = 2023 # Example, ideally dynamic

headers = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY
}

def fetch_transfers(team_id: int):
    """Fetch transfers for a specific team."""
    url = f"{BASE_URL}/transfers"
    params = {"team": team_id}
    logger.info(f"Fetching transfers for team {team_id}...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('response', [])

def flatten_transfers(transfers_data):
    """Flatten the deeply nested JSON transfer data from API-Football."""
    flat_data = []
    for item in transfers_data:
        player = item.get('player', {})
        update = item.get('update', '')
        for transfer in item.get('transfers', []):
            teams = transfer.get('teams', {})
            in_team = teams.get('in', {})
            out_team = teams.get('out', {})
            flat_data.append({
                "player_id": player.get('id'),
                "player_name": player.get('name'),
                "update_time": update,
                "transfer_date": transfer.get('date'),
                "transfer_type": transfer.get('type'),
                "team_in_id": in_team.get('id'),
                "team_in_name": in_team.get('name'),
                "team_out_id": out_team.get('id'),
                "team_out_name": out_team.get('name'),
            })
    return pd.DataFrame(flat_data)

def upload_to_s3(df: pd.DataFrame, filename: str):
    """Upload flattened dataframe to S3 staging bucket."""
    csv_buffer = df.to_csv(index=False)
    s3_client = boto3.client('s3')
    logger.info(f"Uploading {filename} to s3://{S3_BUCKET}/transfers/...")
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=f"transfers/{filename}",
            Body=csv_buffer
        )
        logger.info(f"Successfully uploaded {filename}.")
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise

def main():
    # Example fetching for a single team to demonstrate flattening logic
    # In production, we iterate through leagues -> teams -> transfers
    # Due to API rate limits, this script would handle throttling.
    logger.info("Starting Transfer Data Ingestion Job")
    
    # Example Team ID: 33 (Manchester United)
    team_id = 33 
    
    try:
        raw_transfers = fetch_transfers(team_id)
        if raw_transfers:
            df = flatten_transfers(raw_transfers)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transfers_team_{team_id}_{timestamp}.csv"
            
            # Print sample to local stdout for verification
            print(df.head())
            
            # upload_to_s3(df, filename) # Commented out for local test
            logger.info("Ingestion complete.")
        else:
            logger.info("No transfers found.")
            
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}")

if __name__ == "__main__":
    main()
