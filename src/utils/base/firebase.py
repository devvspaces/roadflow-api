from django.conf import settings
from firebase_admin import auth, credentials, initialize_app

cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
app = initialize_app(cred)


class FirebaseProvider:
    @classmethod
    def verify_token(cls, token: str) -> dict:
        return auth.verify_id_token(token, app=app, check_revoked=True)
