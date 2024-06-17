"""
CREATE NFT

1. Import necessary libraries:

algosdk library is used to interact with the Algorand blockchain.
We will be using algonode API to interact with the Algorand network.

2. Create a new algod client to interact with the Algorand network, using the retrieved API key and connecting to the Algorand test network.

4. Retrieve the mnemonic phrase (i.e., a seed phrase) from an environment variable using the config function.

5. Derive the private key from the mnemonic phrase using the mnemonic.to_private_key function from algosdk.

6. Derive the Algorand address associated with the private key using the account.address_from_private_key function from algosdk.

7. Create an NFT called ESG with a total supply of 1 unit using the transaction.AssetConfigTxn function from algosdk.

The sender is the Algorand address associated with the private key.
The suggested parameters for the transaction are retrieved using the algod_client.suggested_params function.
The NFT is set up such that it is not frozen by default, has a unit name of "ESG", an asset name of "ESG Token", and the creator's address is set as the manager, reserve, freeze, and clawback roles.
A URL is provided where additional information about the NFT can be found.
The number of decimal places for the NFT is set to 0, meaning that it is not divisible.
Sign the transaction using the private key and the sign function from transaction.

8. Send the transaction to the Algorand network using the algod_client.send_transaction function and retrieve the transaction ID (txid).

9. Print the transaction ID.

Optionally, wait for the transaction to be confirmed using the transaction.wait_for_confirmation function from algosdk and print the confirmed round number.

Optionally, retrieve the asset ID of the newly created NFT from the results dictionary returned by wait_for_confirmation function and print it.
"""

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any

# Load the API key from the environment file
api_key = ''

# example: ALGOD_CREATE_CLIENT
# Create a new algod client, configured to connect to our local sandbox
algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient(api_key, algod_address)

mn = 'jungle length act gentle cabin nothing obtain alpha gorilla mimic width diagram element tornado syrup budget diagram rose box pipe prepare gentle field about review'
private_key = mnemonic.to_private_key(mn)
# print(f"Base64 encoded private key: {private_key}")
address = account.address_from_private_key(private_key)
print(f"Address: {address}")

# Account 1 creates an NFT called `ESG` with a total supply
# of 1 units and sets itself to the freeze/clawback/manager/reserve roles
sp = algod_client.suggested_params()
txn = transaction.AssetConfigTxn(
    sender=address,
    sp=sp,
    default_frozen=False,
    unit_name="DDOLAR",
    asset_name="Digital Dollar",
    manager=address,
    reserve=address,
    freeze=address,
    clawback=address,
    url="https://www.weforum.org/reports/annual-report-2021-2022",
    total=10000000,
    decimals=2,
)

# Sign with secret key of creator
stxn = txn.sign(private_key)
# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)
print(f"Sent asset create transaction with txid: {txid}")
# # Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")

# example: ASSET_INFO
# Retrieve the asset info of the newly created asset
asset_info = algod_client.asset_info(created_asset)
asset_params: Dict[str, Any] = asset_info["params"]
print(f"Asset Name: {asset_params['name']}")
print(f"Asset params: {list(asset_params.keys())}")
# example: ASSET_INFO


# example: ASSET_OPTIN
sp = algod_client.suggested_params()
receiver_address = "CGI5X2I3LHDSNIZZOKUONPXK7KXPWJBZDYVO4VXJZRQPUHDW5XPPP3RKDY"
# Create opt-in transaction
# asset transfer from me to me for asset id we want to opt-in to with amt==0
optin_txn = transaction.AssetOptInTxn(
    sender="CGI5X2I3LHDSNIZZOKUONPXK7KXPWJBZDYVO4VXJZRQPUHDW5XPPP3RKDY", sp=sp, index=created_asset
)
signed_optin_txn = optin_txn.sign(private_key="wvJG12J4ZJ+OmpFVEbfbzG9eVqQC95TM/qfipzoPDeIRkdvpG1nHJqM5cqjmvur6rvskOR4q7lbpzGD6HHbt3g==")
txid = algod_client.send_transaction(signed_optin_txn)
print(f"Sent opt in transaction with txid: {txid}")

# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")
# example: ASSET_OPTIN

# example: ASSET_XFER
sp = algod_client.suggested_params()
# Create transfer transaction
xfer_txn = transaction.AssetTransferTxn(
    sender=address,
    sp=sp,
    receiver=receiver_address,
    amt=10000,
    index=created_asset,
)
signed_xfer_txn = xfer_txn.sign(private_key=private_key)
txid = algod_client.send_transaction(signed_xfer_txn)
print(f"Sent transfer transaction with txid: {txid}")

results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")
# example: ASSET_XFER
