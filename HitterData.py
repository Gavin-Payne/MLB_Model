import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import unicodedata
import json


load_dotenv()

google_cloud_service_account_json = os.getenv('GOOGLE_CLOUD_SERVICE_ACCOUNT')

if google_cloud_service_account_json:
    google_cloud_service_account = json.loads(google_cloud_service_account_json)
else:
    raise ValueError("GOOGLE_CLOUD_SERVICE_ACCOUNT environment variable not set")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_cloud_service_account, scopes=scopes)
client = gspread.authorize(creds)

Sheet_ID = os.getenv("Sheet_ID")
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit#gid=478985565')

sheet = sheet.worksheet("Lineups")







url = "https://www.mlb.com/starting-lineups"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Locate the section containing all lineups
lineup_sections = soup.find_all('section', class_='starting-lineups')

team_lineups = []

def remove_accents(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


for section in lineup_sections:
    team_names = section.find_all('div', class_='starting-lineups__team-names')
    if len(team_names) < 2:
        continue
    t = [team.get_text(strip=True) for team in team_names]
    teams = []
    for team in t:
        x = team.split('@')
        teams.append(x[0])
        teams.append(x[1])
    player_list = section.find_all('ol', class_='starting-lineups__team')
    player_list = [player_list[i] for i in range(len(player_list)) if i % 4 < 2]
    if len(teams) != len(player_list):
        print("Mismatch between number of teams and player lists")
        continue
    pitcher_elements = section.find_all('div', class_='starting-lineups__pitcher-name')
    pitcher_names = []
    for pitcher_element in pitcher_elements:
        pitcher_link = pitcher_element.find('a')
        if pitcher_link:
            full_pitcher_name = pitcher_link.get_text(strip=True)
            full_pitcher_name = remove_accents(full_pitcher_name)
            pitcher_names.append(full_pitcher_name)
        else:
            pitcher_names.append("Unknown Pitcher")
    for game_index in range(0, len(teams), 2):
        if game_index + 1 >= len(teams) or len(pitcher_names) <= game_index + 1:
            continue
        team1_name = teams[game_index]
        team2_name = teams[game_index + 1]
        team1_players = player_list[game_index]
        team2_players = player_list[game_index + 1]
        team1_opposing_pitcher = pitcher_names[game_index + 1]
        team2_opposing_pitcher = pitcher_names[game_index]
        team1_data = [remove_accents(team1_name)]
        players = team1_players.find_all('li', class_='starting-lineups__player')
        for player in players:
            player_tag = player.find('a')
            if player_tag:
                player_name = player_tag.get_text(strip=True)
                player_name = remove_accents(player_name)
            else:
                player_name = "Unknown"
            team1_data.append(player_name)
        while len(team1_data) < 10:
            team1_data.append("")
        team1_data.append(f"{team1_opposing_pitcher}")
        team2_data = [remove_accents(team2_name)]
        players = team2_players.find_all('li', class_='starting-lineups__player')
        for player in players:
            player_tag = player.find('a')
            if player_tag:
                player_name = player_tag.get_text(strip=True)
                player_name = remove_accents(player_name)
            else:
                player_name = "Unknown"
            team2_data.append(player_name)
        while len(team2_data) < 10:
            team2_data.append("")
        team2_data.append(f"{team2_opposing_pitcher}")
        if len(team1_data) > 11:
            team1_data = team1_data[:11]
        if len(team2_data) > 11:
            team2_data = team2_data[:11]
        team_lineups.append(team1_data)
        team_lineups.append(team2_data)
last_column_letter = 'K'
sheet.batch_clear([f"A2:{last_column_letter}31"])
sheet.update(range_name=f"A2:{last_column_letter}{len(team_lineups)+1}", values=team_lineups)