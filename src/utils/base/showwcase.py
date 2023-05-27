from urllib.parse import urljoin
from django.conf import settings
import requests

HEADERS = {
    "x-api-key": settings.SHOWWCASE_API_KEY
}


def show_get(endpoint: str):
    url = urljoin(settings.SHOWWCASE_BASE_URL, endpoint)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
