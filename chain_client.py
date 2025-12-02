# chain_client.py
import os
import json
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()


RPC_URL = os.environ["RPC_URL"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]
CHAIN_ID = int(os.environ.get("CHAIN_ID", "11155111"))

w3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

with open("contract_abi.json") as f:
    ABI = json.load(f)
with open("contract_address.txt") as f:
    CONTRACT_ADDRESS = f.read().strip()

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

def send_tx(fn, *args, gas=3000000): 
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = fn.build_transaction({
        "chainId": CHAIN_ID,
        "from": acct.address,
        "nonce": nonce,
        "gas": gas,
        "gasPrice": w3.to_wei('1', 'gwei') 
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def add_document(doc_hash_bytes32, ipfs_cid, issuer, dateIssued, verifier):
    fn = contract.functions.addDocument(doc_hash_bytes32, ipfs_cid, issuer, dateIssued, verifier)
    receipt = send_tx(fn)
    return receipt

def add_version(id, doc_hash_bytes32, ipfs_cid, issuer, dateIssued, verifier):
    fn = contract.functions.addVersion(id, doc_hash_bytes32, ipfs_cid, issuer, dateIssued, verifier)
    receipt = send_tx(fn)
    return receipt

def get_latest(id):
    return contract.functions.getLatest(id).call()

def lookup_by_hash(doc_hash_bytes32):
    return contract.functions.lookupByHash(doc_hash_bytes32).call()
