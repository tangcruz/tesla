import os
import logging
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the scope for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def get_credentials() -> Credentials:
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except ValueError:
            logger.warning(f"Invalid token file. Removing {TOKEN_FILE}")
            os.remove(TOKEN_FILE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                logger.warning("Failed to refresh token. Initiating new authorization flow.")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Missing {CREDENTIALS_FILE}. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_sheets_service():
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

service = get_sheets_service()
sheet = service.spreadsheets()

def read_sheet() -> List[List[str]]:
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:Z1000').execute()
        values = result.get('values', [])
        logger.info(f"Successfully read {len(values)} rows from the sheet")
        return values
    except HttpError as error:
        logger.error(f"An error occurred while reading the sheet: {error}")
        raise

def update_sheet(row: int, col: str, value: Any) -> Dict[str, Any]:
    try:
        body = {'values': [[value]]}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, 
            range=f'{col}{row}',
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        logger.info(f"Successfully updated cell {col}{row} with value: {value}")
        return result
    except HttpError as error:
        logger.error(f"An error occurred while updating the sheet: {error}")
        raise

if __name__ == "__main__":
    if not SPREADSHEET_ID:
        logger.error("GOOGLE_SPREADSHEET_ID environment variable is not set")
        exit(1)
    
    try:
        data = read_sheet()
        print(f"First row of data: {data[0] if data else 'No data'}")
    except Exception as e:
        logger.error(f"Failed to read sheet: {e}")