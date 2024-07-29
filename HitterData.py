import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import unicodedata


load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = os.getenv("Sheet_ID")
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=478985565')

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
    # Find the team names
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
    
    for team_name, team_players in zip(teams, player_list):
        team_data = [team_name] 
        players = team_players.find_all('li', class_='starting-lineups__player')
        for player in players:
            player_tag = player.find('a')
            if player_tag:
                player_name = player_tag.get_text(strip=True)
            else:
                player_name = "Unknown"
            team_data.append(remove_accents(player_name))
        team_lineups.append(team_data)

sheet.update(f"A2:J{len(team_lineups)+1}", team_lineups)