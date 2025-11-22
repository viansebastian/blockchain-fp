import os
import json
from solcx import install_solc, set_solc_version, compile_standard
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

install_solc("0.8.19")
set_solc_version("0.8.19")

RPC_URL = os.environ["RPC_URL"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]
CHAIN_ID = int(os.environ.get("CHAIN_ID", "11155111"))

w3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

print("Deploying from", acct.address)

# Read Solidity source
with open("contracts/DocumentRegistry.sol", "r") as f:
    source = f.read()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"DocumentRegistry.sol": {"content": source}},
        "settings": {
            "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}}
        }
    }
)

contract_interface = compiled["contracts"]["DocumentRegistry.sol"]["DocumentRegistry"]

abi = contract_interface["abi"]
bytecode = contract_interface["evm"]["bytecode"]["object"]

Document = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(acct.address)
gas_est = Document.constructor().estimate_gas({"from": acct.address})

tx = Document.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "from": acct.address,
    "nonce": nonce,
    "gas": gas_est,
    "gasPrice": w3.eth.gas_price
})

signed = acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

print("Sent deploy tx:", tx_hash.hex())

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract deployed at:", receipt.contractAddress)

with open("contract_abi.json", "w") as f:
    json.dump(abi, f)

with open("contract_address.txt", "w") as f:
    f.write(receipt.contractAddress)
