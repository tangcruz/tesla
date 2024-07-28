import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the scope for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1MzDisZn3dDdP33MJvu4lk5U05ukSCcrXqJNN0TXm0oo'

# Google Sheets API authorization
def authorize_google_sheets():
    credentials_dict = json.loads(os.environ.get('GCP_SA_KEY'))
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

service = authorize_google_sheets()
sheet = service.spreadsheets()

# Read data from Google Sheets
def read_sheet():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:Z1000').execute()
    values = result.get('values', [])
    return values

# Update data in Google Sheets
def update_sheet(row, col, value):
    body = {'values': [[value]]}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=f'{col}{row}',
        valueInputOption='USER_ENTERED', body=body).execute()
    return result