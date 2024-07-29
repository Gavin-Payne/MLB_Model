import gspread
from google.oauth2.service_account import Credentials
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

API_Key = os.getenv("API_Key")
sheet_id = os.getenv("Sheet_ID")

def get_ids():
    response = requests.get(f'https://api.the-odds-api.com/v4/sports/baseball_mlb/events?apiKey={API_Key}')
    return response.json()

game_ids = [game['id'] for game in get_ids()]

# Helper function to get odds
def get_odds(id, market):
    response = requests.get(f"https://api.the-odds-api.com/v4/sports/baseball_mlb/events/{id}/odds?apiKey={API_Key}&regions=us&markets={market}&oddsFormat=american")
    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.status_code)
        return None

# function to make data more useable
def flatten_data(data, Used_Names, mi, ma):
    flat_data = []
    for bookmaker in data['bookmakers']:
        for market in bookmaker['markets']:
            for outcome in market['outcomes']:
                if outcome['price'] > mi and outcome['price'] < ma and outcome['name'] == 'Over':
                    if Used_Names.count(outcome['description']) <= 0:
                        flat_data.append([
                            data['id'], data['sport_title'], data['commence_time'], 
                            data['home_team'], data['away_team'], bookmaker['title'], 
                            market['key'], market['last_update'], outcome['name'], outcome['name'], outcome['description'].split()[-1], 
                            outcome['point'], outcome['price']
                        ])
                    Used_Names.append(outcome['description'])
    return flat_data

# Function to update worksheet
def update_worksheet(sheet_name, market, mi, ma):
    sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=478985565').worksheet(sheet_name)
    sheet.clear()

    headers = ['ID', 'Sport Title', 'Commence Time', 'Home Team', 'Away Team', 
            'Bookmaker Key', 'Bookmaker Title', 'Last Update', 'Over/Under', 'Filler',
            'Last Name', 'Outcome Point', 'Outcome Price']
    sheet.insert_row(headers, 1)
    
    all_flattened_data = []
    Used_Names = []

    for id in game_ids:
        data = get_odds(id, market)
        if data:
            flattened_data = flatten_data(data, Used_Names, mi, ma)
            all_flattened_data.extend(flattened_data)

    if all_flattened_data:
        sheet.update(f'A2:M{len(all_flattened_data) + 1}', all_flattened_data)

update_worksheet("OddsAutomationK", "pitcher_strikeouts", -170, 125)
update_worksheet("OddsAutomationH", "pitcher_hits_allowed", -170, 125)
update_worksheet("OddsAutomationPO", "pitcher_outs", -250, 250)

# Update the date in the sheet
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=478985565').worksheet("OddsAutomationK")
sheet.update_cell(1, 16, datetime.today().strftime('%Y-%m-%d'))