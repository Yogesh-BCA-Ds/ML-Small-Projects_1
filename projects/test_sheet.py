import gspread
from google.oauth2.service_account import Credentials
scope = [
"https://googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json",scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Student_data").sheet1
sheet.update("A1","Connected successfully")
print("done")
