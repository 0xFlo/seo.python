#src/api/GoogleOauth2.py
import os
import logging
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError, RefreshError

logging.basicConfig(level=logging.DEBUG)

class GoogleAuthConfig:
    READONLY_SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    PROJECT_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CLIENT_SECRET_FILE_PATH = os.path.join(PROJECT_BASE_DIR, '..', 'secrets', 'client_secrets.json')
    TOKEN_FILE_PATH = os.path.join(PROJECT_BASE_DIR, '..', 'secrets', 'tokens', 'token.json')

class OAuthCredentialManager:
    def __init__(self, token_file_path, scopes):
        self.token_file_path = token_file_path
        self.scopes = scopes

    def get_credentials(self):
        credentials = self._load_from_file()
        if not credentials or not credentials.valid:
            credentials = self._refresh_if_expired(credentials) or self._get_new_credentials()
        return credentials

    def _load_from_file(self):
        try:
            return oauth_credentials.Credentials.from_authorized_user_file(self.token_file_path, self.scopes)
        except (GoogleAuthError, OSError) as e:
            logging.error(f"Error loading credentials: {e}")
            return None

    def _refresh_if_expired(self, credentials):
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                return credentials
            except RefreshError as e:
                logging.error(f"Error refreshing credentials: {e}")
        return None

    def _get_new_credentials(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.token_file_path, self.scopes)
            return flow.run_local_server(port=0)
        except GoogleAuthError as e:
            logging.error(f"Error obtaining new credentials: {e}")
            return None

    def save_to_file(self, credentials):
        os.makedirs(os.path.dirname(self.token_file_path), exist_ok=True)
        try:
            with open(self.token_file_path, 'w') as token_file:
                token_file.write(credentials.to_json())
        except IOError as e:
            logging.error(f"I/O Error saving credentials: {e}")

def google_api_authentication():
    auth_config = GoogleAuthConfig()
    credential_manager = OAuthCredentialManager(auth_config.TOKEN_FILE_PATH, auth_config.READONLY_SCOPES)

    credentials = credential_manager.get_credentials()
    if credentials:
        credential_manager.save_to_file(credentials)

    return credentials