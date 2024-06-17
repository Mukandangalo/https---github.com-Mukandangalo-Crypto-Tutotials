"""
This Python code demonstrates how to connect to the Algorand blockchain, create a transaction, 
sign it with a private key, and submit it to the blockchain using the AlgodClient instance 
provided by the algosdk library. It also shows how to wait for the transaction to be 
confirmed and fetch the transaction information.
"""

"""
1. The script imports necessary libraries like base64, json, algosdk, and decouple.
2. It fetches the API key from the environment variable by using the 'config' method from the decouple library.
3. The script sets up the connection to the Algorand blockchain by creating an instance of the AlgodClient class with the 
   provided API key, Algod address, and headers. It connects to the testnet Algorand blockchain hosted by Algonode.
4. The script fetches the private key from the mnemonic using the mnemonic.to_private_key() method from the algosdk library.
5. The script derives the Algorand address from the private key using the account.address_from_private_key() method from the same library.
6. The script builds an unsigned Payment Transaction object with the suggested parameters received from the AlgodClient instance using the suggested_params() method.
7. The script signs the transaction with the private key.
8. The script submits the signed transaction to the Algorand blockchain using the send_transaction() method from the AlgodClient instance and gets back the transaction ID.
9. The script waits for the transaction to be confirmed using the wait_for_confirmation() method from the transaction module of the algosdk library.
10. Finally, the script prints out the transaction information, such as the transaction ID and the decoded note.
"""


from base64 import b64decode
import json
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

# Load the API key (Algonode does not require an API key hence the empty string)
api_key = ''

# example: ALGOD_CREATE_CLIENT
# Create a new algod client, configured to connect to our local sandbox
algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient(api_key, algod_address)

mn = 'view fence cloud electric solid concert diary erosion cousin bounce express congress unit tooth poverty emotion select join timber wing junk breeze record above pumpkin'
private_key = mnemonic.to_private_key(mn)
# print(f"Base64 encoded private key: {private_key}")
address = account.address_from_private_key(private_key)
print(f"Address: {address}")

# Build Transaction
# grab suggested params from algod using client
# includes things like suggested fee and first/last valid rounds
receiver_address =  "FR53SDMWJIJCT2TK24Q44FCRBNPUQ2R3BXURDWW3MLPC655SOCVPDVLVLU"

params = algod_client.suggested_params()
unsigned_txn = transaction.PaymentTxn(
    sender=address,
    sp=params,
    receiver=receiver_address,
    amt=1000000, # Amount variable is measured in MicroAlgos. i.e. 1 ALGO = 1,000,000 MicroAlgos
    note="My loan balance",
)

# sign the transaction
signed_txn = unsigned_txn.sign(private_key)

# submit the transaction and get back a transaction id
txid = algod_client.send_transaction(signed_txn)
print("Successfully submitted transaction with txID: {}".format(txid))

# wait for confirmation
txn_result = transaction.wait_for_confirmation(algod_client, txid)

print(f"Transaction information: {json.dumps(txn_result, indent=4)}")
print(f"Decoded note: {b64decode(txn_result['txn']['txn']['note'])}")