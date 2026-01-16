from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def get_creds_from_ctx(tool_context):
    sess = tool_context.session  
    key = "google_oauth:unified_scopes"
    data = sess.state.get(key)
    if not data:
        raise RuntimeError("OAuth not initialized in session")

    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )

    if not creds.valid and creds.refresh_token:
        try:
            creds.refresh(Request())
            data.update({"token": creds.token})
            sess.state[key] = data
        except Exception:
            pass

    return creds
