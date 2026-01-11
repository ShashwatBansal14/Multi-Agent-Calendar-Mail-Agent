from googleapiclient.discovery import build
from tools.auth_manager import get_credentials


def list_files(limit=10):
    """
    Lists files from the user's Google Drive.
    Returns basic metadata only (safe & read-only).
    """

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    results = service.files().list(
        pageSize=limit,
        fields="files(id, name, webViewLink)"
    ).execute()

    files = results.get("files", [])

    drive_files = []
    for idx, file in enumerate(files, start=1):
        drive_files.append({
            "id": str(idx),
            "name": file["name"],
            "link": file.get("webViewLink")
        })

    return drive_files
