import os
import io
from datetime import datetime
import pytz
import tempfile
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.adk.agents.llm_agent import LlmAgent
from google.auth.transport.requests import Request

load_dotenv()
oauth_token_cache = {}

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# Scope for reading files
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_credentials_interactive():
    creds = oauth_token_cache.get("drive")
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        oauth_token_cache["drive"] = creds
        return creds
            
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://127.0.0.1:8000/dev-ui/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    creds = flow.run_local_server(prompt='consent')
    oauth_token_cache["drive"] = creds
    return creds

def get_drive_client():
    creds = get_drive_credentials_interactive()
    return build("drive", "v3", credentials=creds)

def search_files(query_name: str):
    """Searches for files by name and returns a list of matches with ID and Name."""
    service = get_drive_client()
    # Simple search query for name contains
    q = f"name contains '{query_name}' and trashed = false"
    results = service.files().list(
        q=q, pageSize=10, fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    
    if not items:
        return f"No files found matching '{query_name}'."
    
    # Return string representation for the LLM
    result_str = "Found files:\n"
    for item in items:
        result_str += f"Name: {item['name']}, ID: {item['id']}, Type: {item['mimeType']}\n"
    return result_str

def download_file(file_id: str, file_name: str):
    """Downloads a file by ID to a local temp directory and returns the file path."""
    service = get_drive_client()
    request = service.files().get_media(fileId=file_id)
    
    # Create a temp file to store the download
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file_name)
    
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        
    return f"File downloaded successfully to: {file_path}"

def get_current_datetime():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

drive_subagent = LlmAgent(
    model="gemini-2.0-flash",
    name="DriveAgent",
    instruction="""You are DriveAgent, responsible for finding and retrieving files from the user's Google Drive.

    IMPORTANT: Current date and IST time is: {get_current_datetime()}

    Your capabilities:
    1. **Search Files**: Use `search_files` to find files by name. Always search first if the user provides a filename.
    2. **Download Files**: Use `download_file` to download a specific file to a local temporary path.
    
    Workflow for sending attachments:
    - If the user wants to send a file, you MUST first find it, then download it.
    - RETURN the local file path provided by the `download_file` tool in your final response so the EmailAgent can use it.
    
    Output Format:
    - If a file is downloaded, explicitly state: "File ready at: [path]"
    - If multiple files are found, ask the user to clarify which ID to download.
    
    Do not hallucinate file paths. Only use paths returned by the download tool.
    """,
    tools=[search_files, download_file, get_current_datetime],
    output_key="drive_summary"
)