import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

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