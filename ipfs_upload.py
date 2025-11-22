# ipfs_upload.py
import os
import requests
import ipfshttpclient
from dotenv import load_dotenv
load_dotenv()

PINATA_KEY = os.environ.get("PINATA_API_KEY")
PINATA_SECRET = os.environ.get("PINATA_API_SECRET")

def upload_to_pinata(filepath, filename=None):
    if not PINATA_KEY or not PINATA_SECRET:
        raise RuntimeError("Pinata keys not set")
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_KEY,
        "pinata_secret_api_key": PINATA_SECRET
    }
    with open(filepath, "rb") as f:
        files = {"file": (filename or os.path.basename(filepath), f)}
        r = requests.post(url, files=files, headers=headers)
    r.raise_for_status()
    return r.json()["IpfsHash"]  # CID

def upload_local_ipfs(filepath):
    client = ipfshttpclient.connect()  # expects a local IPFS daemon running
    res = client.add(filepath)
    # res is dict {'Hash': '...', 'Name': '...'}
    return res["Hash"]
