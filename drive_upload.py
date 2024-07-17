
import io
import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

def get_folder_id(service, folder_name,parent_id='15ZuPJreNH3asngPduuUHa0ZYg_aReaeu'):
    try:
        # Search for the folder by name
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = response.get('files', [])
        if files:
            # Return the ID of the folder if it exists
            return files[0]['id']
        else:
            # If folder does not exist, create it
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_id:
                file_metadata["parents"] = [parent_id]

            folder = service.files().create(body=file_metadata, fields="id").execute()
            return folder.get('id')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

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
    folder_id = get_folder_id(service,'Pitch Summaries')

    file_metadata = {
        # Name of file to save as
        "name": "summarized_data.csv",
        # ID of the parent folder in Google Drive
        "parents": [folder_id]

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

def extract_file_id(slides_url):
    """Extract the file ID from a Google Slides URL."""
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', slides_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Slides URL")

def download_presentation(service, file_id, file_name, mime_type):
    """Download a Google Slides presentation."""
    request = service.files().export_media(fileId=file_id, mimeType=mime_type)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f'Download {int(status.progress() * 100)}%.')

def download_slide(slide_url,service):
    try:
        file_id = extract_file_id(slide_url)
        print(f'File ID: {file_id}')
        file_metadata = service.files().get(fileId=file_id, fields='name').execute()
        file_name = file_metadata.get('name', 'presentation') + '.pdf'
        # Download the presentation as a PDF
        download_presentation(service, file_id, file_name, 'application/pdf')
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")





