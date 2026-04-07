import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings

class AuthService:
    def verify_google_token(self, token: str):
        """Verifies a Google ID token and returns user info."""
        try:
            # Specify the GOOGLE_CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo['sub']
            return idinfo
        except ValueError:
            # Invalid token
            return None

auth_service = AuthService()
