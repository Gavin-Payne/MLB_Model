import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv

def determine_handedness(full_name):
    """
    Determine pitcher handedness based on asterisk in name
    * = Left-handed (L)
    No asterisk = Right-handed (R)
    """
    if not isinstance(full_name, str):
        return ""
    
    if '*' in full_name:
        return "L"  # Left-handed
    else:
        return "R"  # Right-handed

def process_google_sheet(sheet_name='Pitcher'):
    """Process names in column B and put handedness in column E"""
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
        
        # Get all values from column B (names)
        col_b_values = worksheet.col_values(2)  
        handedness = [determine_handedness(name) for name in col_b_values]
        
        # Update column E with handedness
        cells = []
        for i, hand in enumerate(handedness, start=1):
            cells.append(gspread.Cell(i, 5, hand))  
        worksheet.update_cells(cells)
        
        print(f"Successfully added handedness for {len(handedness)} pitchers in '{sheet_name}' sheet.")
        print(f"Left-handed pitchers: {handedness.count('L')}")
        print(f"Right-handed pitchers: {handedness.count('R')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sheet_name = input("Enter the sheet name (press Enter for default 'Pitcher'): ")
    if not sheet_name:
        sheet_name = "Pitching"
    
    process_google_sheet(sheet_name)