import gspread
from google.oauth2.service_account import Credentials
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import unicodedata
import re
from collections import defaultdict

load_dotenv()

google_cloud_service_account_json = os.getenv('GOOGLE_CLOUD_SERVICE_ACCOUNT')

if google_cloud_service_account_json:
    google_cloud_service_account = json.loads(google_cloud_service_account_json)
else:
    raise ValueError("GOOGLE_CLOUD_SERVICE_ACCOUNT environment variable not set")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_cloud_service_account, scopes=scopes)
client = gspread.authorize(creds)

API_Key = os.getenv("API_Key")
Sheet_ID = os.getenv("Sheet_ID")

def regularize_name(name):
    """Clean and standardize player names."""
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r"[''`]", "", name)
    name = re.sub(r"[-]", " ", name)
    name = re.sub(r"[^a-zA-Z\s]", "", name)
    name_parts = name.split()
    suffixes = {"jr", "sr", "ii", "iii", "iv", "v"}
    if name_parts and name_parts[-1].lower() in suffixes:
        name_parts.pop()
    name_parts = [part.capitalize() for part in name_parts]
    
    # Return the full name instead of just the last name
    if name_parts:
        return " ".join(name_parts)
    return ""

def get_ids():
    """Get MLB game IDs from the API."""
    response = requests.get(f'https://api.the-odds-api.com/v4/sports/baseball_mlb/events?apiKey={API_Key}')
    return response.json()

game_ids = [game['id'] for game in get_ids()]

def get_odds(id, market):
    """Get odds for a specific market for a game ID."""
    response = requests.get(f"https://api.the-odds-api.com/v4/sports/baseball_mlb/events/{id}/odds?apiKey={API_Key}&regions=us2&markets={market}&oddsFormat=american")
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error getting odds for {id}, market {market}: {response.status_code}')
        return None

def flatten_data(data, price_range=None):
    """
    Extract odds data from FLIFF bookmaker, including both Over and Under lines.
    Returns a dictionary with player names as keys and [line, price, over_under] as values.
    """
    flat_data = defaultdict(list)
    
    for bookmaker in data['bookmakers']:
        if bookmaker["key"] == 'fliff':  # Only use data from FLIFF
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    price = outcome['price']
                    if price_range and (price < price_range[0] or price > price_range[1]):
                        continue
                        
                    name = regularize_name(outcome['description'])
                    over_under = outcome['name']  # "Over" or "Under"
                    
                    player_key = f"{name} {over_under}"
                    flat_data[player_key] = [outcome['point'], price, over_under]
    
    return flat_data

def update_worksheet(sheet_name, market, price_range=None):
    """Update worksheet with odds data for specified market."""
    sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit#gid=478985565').worksheet(sheet_name)
    sheet.batch_clear(["A1:C1000"])  
    headers = ['Player', 'Type', 'Line', 'Price']
    sheet.update(values=[headers], range_name='A1')
    
    cumulative = []
    
    for game_id in game_ids:
        data = get_odds(game_id, market)
        if data:
            flattened_data = flatten_data(data, price_range)
            if flattened_data:
                rows = []
                for player_key, values in flattened_data.items():

                    full_name = player_key.rsplit(' ', 1)[0]
                    over_under = values[2]  # Type is the 3rd element
                    line = values[0]        # Line is the 1st element
                    price = values[1]       # Price is the 2nd element

                    rows.append([full_name, over_under, line, price])
                cumulative.extend(rows)
    
    if cumulative:
        sheet.update(values=cumulative, range_name="A2")  
        print(f"Updated {sheet_name} with {len(cumulative)} rows of data for {market}")
    else:
        print(f"No data found for {market} from FLIFF")

# Update worksheets with different markets and price ranges
update_worksheet("OddsAutomationK", "pitcher_strikeouts", [-200, 200])
#update_worksheet("OddsAutomationH", "pitcher_hits_allowed", [-200, 200])
update_worksheet("OddsAutomationPO", "pitcher_outs", [-300, 300])

sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit#gid=478985565').worksheet("OddsAutomationK")
sheet.update_cell(1, 5, datetime.today().strftime('%Y-%m-%d'))