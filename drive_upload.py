
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_basic(file):
  """Insert new file.
  Returns : Id's of the file uploaded
  Load pre-authorized user credentials from the environment.
  for guides on implementing OAuth2 for the application.
  """
  SCOPES = ['https://www.googleapis.com/auth/drive']

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  
  try:
    # create drive api client
    service = build("drive", "v3",credentials=creds)

    file_metadata = {
        # Name of file to save as
        "name": "summarized_data.csv",
        # ID of the parent folder in Google Drive
        "parents": ['15ZuPJreNH3asngPduuUHa0ZYg_aReaeu']

    }
    media = MediaFileUpload(file, mimetype="text/csv")

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")


