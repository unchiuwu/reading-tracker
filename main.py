import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = os.getenv("SHEET_ID")
sheet = client.open_by_key(sheet_id).worksheet("Public")
values = sheet.get_all_values()
data = sheet.get_all_records()
df = pd.DataFrame(data)

print(df.head())
print(df.info())