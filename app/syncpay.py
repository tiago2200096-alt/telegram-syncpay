import os
import time
import requests

SYNC_BASE_URL = os.getenv("SYNC_BASE_URL", "https://api.syncpayments.com.br").rstrip("/")
SYNC_CLIENT_ID = os.getenv("SYNC_CLIENT_ID", "")
SYNC_CLIENT_SECRET = os.getenv("SYNC_CLIENT_SECRET", "")
SYNC_WEBHOOK_URL = os.getenv("SYNC_WEBHOOK_URL", "").strip()

_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def get_sync_token():
    now = time.time()

    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 30:
        return _token_cache["access_token"]

    url = f"{SYNC_BASE_URL}/api/partner/v1/auth-token"
    payload = {
        "client_id": SYNC_CLIENT_ID,
        "client_secret": SYNC_CLIENT_SECRET
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    access_token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in

    return access_token


def create_pix_payment(amount, description, client_name, cpf, email, phone):
    token = get_sync_token()

    url = f"{SYNC_BASE_URL}/api/partner/v1/cash-in"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "amount": amount,
        "description": description,
        "client": {
            "name": client_name,
            "cpf": cpf,
            "email": email,
            "phone": phone
        }
    }

    if SYNC_WEBHOOK_URL:
        payload["webhook_url"] = SYNC_WEBHOOK_URL

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()


def get_transaction_status(identifier):
    token = get_sync_token()

    url = f"{SYNC_BASE_URL}/api/partner/v1/transaction/{identifier}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()
