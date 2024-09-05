from flask import Flask, render_template, jsonify
import subprocess
from waitress import serve
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
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
sh = sheet.worksheet("Calc")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_python_program')
def run_python_program():
    sh = sheet.worksheet("Calc")
    names = sh.get("B5:B34")
    names = [item for sublist in names for item in sublist]
    
    CalcTable = pd.DataFrame(sh.get("H5:S34"))
    
    
    if len(names) != CalcTable.shape[0]:
        if len(names) > CalcTable.shape[0]:
            names = names[:CalcTable.shape[0]]
        else:
            CalcTable = CalcTable.iloc[:len(names)]
    

    CalcTable.index = names
    CalcTable.replace(['#N/A', '#VALUE!'], np.nan, inplace=True)
    CalcTable = CalcTable.apply(pd.to_numeric, errors='coerce') 
    CalcTable.fillna(0, inplace=True)
    CalcTable = CalcTable.loc[~(CalcTable == 0).all(axis=1)]

    plt.figure(figsize=(16, 12))
    sns.heatmap(CalcTable, annot=True)
    plt.title('Binomial Strikeout Distribution')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    result = subprocess.run(['python3', 'MLB.py'], capture_output=True, text=True)

    return jsonify({
        'message': result.stdout,
        'image': img_base64
    })

@app.route('/history')
def history():
    sh = sheet.worksheet("Results")
    df = pd.DataFrame(sh.get("B27:F2000"))
    df.columns = ['Date',	'w/l',	'odds',	'Units risked',	'implied odds:']
    def highlight_high_scores(val):
        if val == 'w':
            color = 'background-color: green'
        elif val == "l":
            color = 'background-color: #ffcccc'
        elif val == ".":
            color = 'background-color: grey'
        else:
            color = 'background-color: white'
        return color

    styled_df = df.style.applymap(highlight_high_scores, subset=['w/l'])

    table_html = styled_df.to_html()
    return render_template('history.html', table_data=table_html)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8000)
