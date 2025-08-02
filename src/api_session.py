import os
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

def api_get(path, params=None):
    """
    Makes a GET request using the shared session.
    If a full URL is provided, it is used as is.
    Otherwise, it's joined with the BASE_URL.
    """

    if not path.startswith(("http://", "https://")):
        path = urljoin(API_ENDPOINT, path)

    return session.get(path, params=params)