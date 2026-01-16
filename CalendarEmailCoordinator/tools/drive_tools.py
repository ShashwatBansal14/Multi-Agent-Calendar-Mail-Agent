import os
import tempfile
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from ..auth import get_unified_credentials

def get_drive_service():
    creds = get_unified_credentials()
    return build('drive', 'v3', credentials=creds)

def search_pdfs(query: str):
    """
    Searches for PDF files in Google Drive matching the query.
    Returns a list of files with ID and Name.
    """
    service = get_drive_service()
    q = f"name contains '{query}' and mimeType='application/pdf' and trashed=false"
    
    results = service.files().list(
        q=q, pageSize=5, fields="nextPageToken, files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if not items:
        return "No PDF files found matching that name."
    
    result_str = "Found these PDFs:\n"
    for item in items:
        result_str += f"- Name: {item['name']} (ID: {item['id']})\n"
    return result_str

def download_pdf_to_temp(file_id: str, file_name: str):
    """
    Downloads a specific file from Drive to a temporary local path.
    Returns the local file path.
    """
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file_name)
    
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    return file_path