import os
import requests
from dotenv import load_dotenv

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
    raise RuntimeError("Pinata API keys are not set")

def upload_bytes(filename: str, content: bytes) -> str:
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    files = {
        "file": (filename, content)
    }

    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
    }

    res = requests.post(url, files=files, headers=headers)

    if res.status_code != 200:
        raise RuntimeError(f"Pinata upload failed: {res.status_code} {res.text}")

    ipfs_hash = res.json()["IpfsHash"]
    return ipfs_hash
