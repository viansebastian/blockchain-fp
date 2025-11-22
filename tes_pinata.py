# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# PINATA_API_KEY = os.getenv("PINATA_API_KEY")
# PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

# url = "https://api.pinata.cloud/data/testAuthentication"

# print(PINATA_API_KEY)
# print(PINATA_API_SECRET)
# headers = {
#     "pinata_api_key": PINATA_API_KEY,
#     "pinata_secret_api_key": PINATA_API_SECRET
# }

# res = requests.get(url, headers=headers)

# print("Status:", res.status_code)
# print("Response:", res.json())

from solcx import get_installed_solc_versions
print(get_installed_solc_versions())