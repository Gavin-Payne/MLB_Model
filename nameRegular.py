import gspread
from google.oauth2.service_account import Credentials
import unidecode
import os
import json
from dotenv import load_dotenv

def regularize_last_name(full_name):
    """Extract the last name, remove asterisks and accents and such"""
    if not isinstance(full_name, str):
        return ""

    parts = str(full_name).split()
    if not parts:
        return ""
    
    last_name = full_name
    
    # Remove asterisks
    last_name = last_name.replace("*", "")
    
    # Remove accents
    last_name = unidecode.unidecode(last_name)
    
    return last_name

def process_google_sheet(sheet_name='Pitcher'):
    """Process names in column B and put regularized last names in column C"""
    try:
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
        spreadsheet = client.open_by_url(f'https://docs.google.com/spreadsheets/d/{Sheet_ID}/edit')
        worksheet = spreadsheet.worksheet(sheet_name)
        
        col_b_values = worksheet.col_values(2)  
        last_names = [regularize_last_name(name) for name in col_b_values]
        
        cells = []
        for i, last_name in enumerate(last_names, start=1):
            cells.append(gspread.Cell(i, 3, last_name))  
        worksheet.update_cells(cells)
        
        print(f"Successfully processed {len(last_names)} names in '{sheet_name}' sheet.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sheet_name = input("Enter the sheet name (press Enter for default 'Pitcher'): ")
    if not sheet_name:
        sheet_name = "Pitching"
    
    process_google_sheet(sheet_name)
    