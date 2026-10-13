# src/connections/alphabet.py
import os
import time
import shutil
import logging
import webbrowser
import wsgiref.simple_server
import wsgiref.util

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    import gspread
except Exception as e:
    logging.warning(f"Unable to import Google dependencies - Google Sheets integration unavailable.")

CURRENT_AUTH_URL = None  # Most recent auth link, for the reopen button

# Scopes: read/write spreadsheets + drive (needed by gspread.openall)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Establish basic local paths
TOKEN_DIR = os.path.expanduser("~/.config/invoicebuddy/")
TOKEN_PATH = os.path.join(TOKEN_DIR, "google_token.json")
SECRETS_PATH = os.path.join(TOKEN_DIR, "client_secrets.json")


class _CallbackCatcher:
    """Tiny WSGI app that records Google's redirect after sign-in."""

    def __init__(self):
        self.last_request_uri = None

    def __call__(self, environ, start_response):
        self.last_request_uri = wsgiref.util.request_uri(environ)
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"Authorization complete. You may close this window."]


def has_saved_token():
    """Check local token file only — no Google contact."""
    return os.path.exists(TOKEN_PATH)


def delete_token():
    """Remove the cached Google token. Keeps client_secrets.json intact."""
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
        logging.info("Google token deleted.")
        return True
    except Exception as e:
        logging.error(f"Could not delete token: {e}")
        return False


def google_connect(secrets_path, cancel_event=None):
    """
    Run the browser OAuth flow using a client_secrets.json file.
    Returns a gspread client on success, None on failure or cancellation.
    Mirrors InstalledAppFlow.run_local_server(), but with cancel support
    and a persistent auth URL for reopening the browser.
    """
    global CURRENT_AUTH_URL

    try:
        os.makedirs(TOKEN_DIR, exist_ok=True)

        # Cache a copy of the secrets file so re-auth never needs it again
        if os.path.abspath(secrets_path) != os.path.abspath(SECRETS_PATH):
            shutil.copy2(secrets_path, SECRETS_PATH)

        flow = InstalledAppFlow.from_client_secrets_file(SECRETS_PATH, SCOPES)

        # ===== Our own callback server (same as run_local_server does) =====
        wsgi_app = _CallbackCatcher()
        local_server = wsgiref.simple_server.make_server(
            "localhost", 0, wsgi_app)

        flow.redirect_uri = f"http://localhost:{local_server.server_port}/"
        auth_url, _ = flow.authorization_url(access_type='offline')
        CURRENT_AUTH_URL = auth_url  # Saved for the reopen button

        webbrowser.open(auth_url)
        logging.info(f"Authorize at: {auth_url}")

        # ===== Wait loop: checks cancel + 10-minute deadline each tick =====
        local_server.timeout = 2  # handle_request() gives up every 2s
        deadline = time.time() + 600

        while not wsgi_app.last_request_uri:
            if cancel_event and cancel_event.is_set():
                local_server.server_close()
                logging.info("OAuth cancelled by user.")
                return None
            if time.time() > deadline:
                local_server.server_close()
                logging.warning("OAuth timed out after 10 minutes.")
                return None
            local_server.handle_request()

        local_server.server_close()

        # Callback arrived — exchange the code for tokens
        authorization_response = wsgi_app.last_request_uri.replace("http", "https")
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials

        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())

        logging.info("Google OAuth successful, token cached.")
        return gspread.authorize(creds)

    except Exception as e:
        logging.error(f"Google OAuth flow failed: {e}")
        return None


def list_spreadsheets(client, limit=3):
    """Return up to `limit` spreadsheet titles as proof of connection."""
    try:
        return [s.title for s in client.openall()][:limit]
    except Exception as e:
        logging.warning(f"Could not list spreadsheets: {e}")
        return []
