import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from dotenv import load_dotenv
import os
import json
import tweepy
import sqlite3

load_dotenv()





google_cloud_service_account_json = os.getenv('GOOGLE_CLOUD_SERVICE_ACCOUNT')

twitterKey = os.getenv("TWITTER_KEY")
twitterSecretKey = os.getenv("TWITTER_SECRET_KEY")
twitterAccessToken = os.getenv("TWITTER_ACCESS_TOKEN")
twitterSecretAccessToken = os.getenv("TWITTER_SECRET_ACCESS_TOKEN")
twitterBearerToken = os.getenv("TWITTER_BEARER_TOKEN")

if google_cloud_service_account_json:
    google_cloud_service_account = json.loads(google_cloud_service_account_json)
else:
    raise ValueError("GOOGLE_CLOUD_SERVICE_ACCOUNT environment variable not set")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_cloud_service_account, scopes=scopes)
client = gspread.authorize(creds)

Sheet_ID = os.getenv("Sheet_ID")
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit#gid=478985565')

sheet = sheet.worksheet("OddsAutomationK")

os.system('python HitterData.py')

sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit#gid=478985565')
sh = sheet.worksheet("Calc")
Names = sh.col_values(2)[4:34]
SamplesSize = []
#Strikeout Lists
Kplays = []
MinimumKOOdds = []
MinimumKUOdds = []
KLine = []
KOOdds = []
KUOdds = []
KUnits = []

#Hits Allowed Lists
Hplays = []
MinimumHOOdds = []
MinimumHUOdds = []
HLine = []
HOOdds = []
HUOdds = []
HUnits = []


def find_image_path(folder, filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'.png', '.jpeg', '.jpg'}  # Default allowed extensions
    filename = filename[1:]
    for ext in allowed_extensions:
        file_path = os.path.join(folder, f"{filename}{ext}")
        print(f"Checking file path: {file_path}")
        if os.path.isfile(file_path):
            return file_path

    return None 

def post_tweet(postPlay, filename, Numbers):
    folder = "PitcherPictures"
    
    today = date.today()

    month_day = today.strftime("%m/%d")
    
    # Find the image path
    image_path = find_image_path(folder, filename)
    if image_path is None:
        print(f"No image file found for {filename}")
        return
    
    try:
        # OAuth1 for media upload (v1.1)
        auth = tweepy.OAuth1UserHandler(twitterKey, twitterSecretKey, twitterAccessToken, twitterSecretAccessToken)
        api = tweepy.API(auth)
        
        # Upload media using v1.1 API
        media = api.media_upload(image_path)
        media_id = media.media_id_string
        
        # OAuth2 for posting tweet (v2)
        client = tweepy.Client(bearer_token=twitterBearerToken, 
                               consumer_key=twitterKey, 
                               consumer_secret=twitterSecretKey, 
                               access_token=twitterAccessToken, 
                               access_token_secret=twitterSecretAccessToken)

        # Prepare tweet content
        confirmation, name, blank, odds = postPlay
        name = name.split()
        if name[2] == "O":
            name[2] = 'Over'  
        else:
            name[2] == 'Under'
        name = " ".join(name)    
        
        if int(odds) > 0:
            odds = '+' + str(odds)
        tweet_text = f"""MLB Strikeout play for {month_day}: {name} K's {odds}
        
    Opponent = {Numbers[1]}
    Projected K% on outs = {Numbers[2]}
    Projected Pitcher outs = {Numbers[3]}
    Projected K's = {Numbers[4]}"""

        # Post tweet with media using v2 API
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        print(f"Tweeted: {tweet_text}")
        
    except tweepy.TweepyException as e:
        print(f"An error occurred: {e}")


#float function for KLine
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    
    
#functions for initiallizing MinimumKOOdds, MinimumKUOdds, SampleSize, KLine, KUOdds, KOOdds, MinimumHOOdds, MinimumHUOdds, HLine, HUOdds, and HOOdds
for i,n in enumerate(sh.col_values(20)[4:34]):
    if n[1:].isnumeric():
        if int(n) > 0:
            MinimumKOOdds.append(int(n)-100)
        else:
            MinimumKOOdds.append(int(n)+100)
    else:
        MinimumKOOdds.append(10000)
        
for i,n in enumerate(sh.col_values(21)[4:34]):
    if n[1:].isnumeric():
        if int(n) > 0:
            MinimumKUOdds.append(int(n)-100)
        else:
            MinimumKUOdds.append(int(n)+100)
    else:
        MinimumKUOdds.append(10000)
        
for i,n in enumerate(sh.col_values(22)[4:34]):
    if n[1:].isnumeric():
        if int(n) > 0:
            KOOdds.append(int(n)-100)
        else:
            KOOdds.append(int(n)+100)
    else:
        KOOdds.append(0)
        
for i,n in enumerate(sh.col_values(23)[4:34]):
    if n[1:].isnumeric():
        if int(n) > 0:
            KUOdds.append(int(n)-100)
        else:
            KUOdds.append(int(n)+100)
    else:
        KUOdds.append(0)
        
for i,n in enumerate(sh.col_values(24)[4:34]):
    if n.isnumeric():
        SamplesSize.append(int(n))
    else:
        SamplesSize.append(0)
        
for i,n in enumerate(sh.col_values(7)[4:34]):
    if isfloat(n):
        KLine.append(float(n))
    else:
        KLine.append(-1)
        
for i,n in enumerate(sh.col_values(20)[75:105]):
    if n[1:].isnumeric():
        if int(n) > 0:
            MinimumHOOdds.append(int(n)-100)
        else:
            MinimumHOOdds.append(int(n)+100)
    else:
        MinimumHOOdds.append(10000)
        
for i,n in enumerate(sh.col_values(21)[75:105]):
    if n[1:].isnumeric():
        if int(n) > 0:
            MinimumHUOdds.append(int(n)-100)
        else:
            MinimumHUOdds.append(int(n)+100)
    else:
        MinimumHUOdds.append(10000)
        
for i,n in enumerate(sh.col_values(22)[75:105]):
    if n[1:].isnumeric():
        x = 0
        if int(n) > 0:
            HUOdds.append(-1*int(n)+75)
        elif int(n) >= -120:
            HUOdds.append(-140-int(n))
        else:
            HUOdds.append(-1*int(n)-120)
        if int(n) > 0:
            HOOdds.append(int(n)-100)
        else:
            HOOdds.append(int(n)+100)
    else:
        HOOdds.append(0)
        HUOdds.append(0)
            
            
for i,n in enumerate(sh.col_values(7)[75:105]):
    if isfloat(n):
        HLine.append(float(n))
    else:
        HLine.append(-1)
        
samplemin = 100

for i,n in enumerate(Names):
    if SamplesSize[i] > samplemin:
        if KOOdds[i] - MinimumKOOdds[i] >= 50:
            Kplays.append([f'{n} O {KLine[i]}', KOOdds[i]])
        elif KUOdds[i] - MinimumKUOdds[i] >= 50:
            Kplays.append([f'{n} U {KLine[i]}', KUOdds[i]])
        if HOOdds[i] - MinimumHOOdds[i] >= 50:
            Hplays.append([f'{n} O {HLine[i]}', HOOdds[i]])
        elif HUOdds[i] - MinimumHUOdds[i] >= 50:
            Hplays.append([f'{n} U {HLine[i]}', HUOdds[i]])

sh = sheet.worksheet("Results")

for i in range(len(Kplays)):
    Odds = Kplays[i][1]
    if Odds >= 0:
        Odds += 100
        Kplays[i].append(str(round(100/Odds, 2)))
    else:
        Odds -= 100
        Kplays[i].append(str(round(-.01*Odds, 2)))
        
for i in range(len(Hplays)):
    Odds = Hplays[i][1]
    if Odds >= 0:
        Odds += 100
        Hplays[i].append(str(round(100/Odds, 2)))
    else:
        Odds -= 100
        Hplays[i].append(str(round(-.01*Odds, 2)))




sh.batch_clear(["B6:G26", "V6:AA26"])

for i, n in enumerate(Kplays):
    i += 6
    sh.update_cell(i, 2, n[0])
    if n[1] >= 0:
        sh.update_cell(i, 4, n[1]+100)
    else:
        sh.update_cell(i, 4, n[1]-100)
    
for i, n in enumerate(Hplays):
    i += 6
    sh.update_cell(i, 22, n[0])
    if n[1] >= 0:
        sh.update_cell(i, 24, n[1]+100)
    else:
        sh.update_cell(i, 24, n[1]-100)
print("Strikeout Props:\n\n" + "\n".join([f'{Kplays[i][0]}   {Kplays[i][2]} U' for i in range(len(Kplays))])) 


# ConfirmedPlays = sh.batch_get([f"A6:D{5+len(Kplays)}"])
# ConfirmedPlays = ConfirmedPlays[0]

# sh = sheet.worksheet("Calc")

# PitcherStats = sh.get("B5:U34")

# for play in ConfirmedPlays:
#     if play[0] == 'Lineup confirmed':
#         post = add_name_if_not_exists(play[1][:-6])
#         if post:
#             for i in range(len(PitcherStats)):
#                 if play[1][:-6] == PitcherStats[i][0]:
#                     post_tweet(play, play[1][:-6], PitcherStats[i])
#                     break
        







