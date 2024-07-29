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

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = os.getenv("Sheet_ID")
sheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=478985565')
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
    
    
    # Check if the number of names matches the number of rows
    if len(names) != CalcTable.shape[0]:
        # Adjust the number of names or rows to match
        if len(names) > CalcTable.shape[0]:
            # More names than rows: truncate names list
            names = names[:CalcTable.shape[0]]
        else:
            # More rows than names: truncate dataframe
            CalcTable = CalcTable.iloc[:len(names)]
    

    CalcTable.index = names
    CalcTable.replace(['#N/A', '#VALUE!'], np.nan, inplace=True)
    CalcTable = CalcTable.apply(pd.to_numeric, errors='coerce')  # Ensure to handle conversion issues
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
    df = pd.DataFrame(sh.get("B27:F1000"))
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

    # Apply the formatting to the DataFrame
    styled_df = df.style.applymap(highlight_high_scores, subset=['w/l'])

    # Convert the styled DataFrame to HTML
    table_html = styled_df.to_html()
    return render_template('history.html', table_data=table_html)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8000)