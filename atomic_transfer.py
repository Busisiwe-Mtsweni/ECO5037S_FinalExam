

from algosdk import account, mnemonic
from typing import Dict, Any
from algosdk import transaction
from algosdk.v2client import algod



# Connect Client # Create a new algod client, configured to connect to a public nodes 
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)



#Create a function to create accounts
def create_accounts(no_accounts):
    accounts = []

    for _ in range(no_accounts):
        try:
            private_key, address = account.generate_account()
            mnemonic_phrase = mnemonic.from_private_key(private_key)

            accounts.append({
                'address': address,
                'private_key': private_key,
                'mnemonic': mnemonic_phrase
            })
        except Exception as e:
            print(f"An error occurred: {e}")

    return accounts

# Create two new accounts for  user A and user B. 
created_accounts = create_accounts(2)
print(created_accounts)


# Store User A and User B mnemonics as mn
mn_A = 'crazy catalog wrap combine away raise rhythm horn control oven crack alert travel drastic elite industry frozen frame volcano mystery wealth obey wedding above diesel'
mn_B = 'narrow drift vast snap whip food carpet mix grit outer sad slide lumber misery echo tiny crush lottery correct split stomach bone practice about dry'

# Store User A and User B private keys as pk 
pk_A =   mnemonic.to_private_key(mn_A)
pk_B = mnemonic.to_private_key(mn_B)

# Store User A and User B address as addr

addr_A = 'FJXDEHMOM3VDPUQOJVNBD3RDRXJRTDBM3VN6LY2ME2XPUTCNHMI5HX3BVQ'
addr_B = 'ETI376GHOBXXZUACC6OIDCB66T7MXTZI2QTTAKY2SAEL3QP5VHCREY6EOE'


# -------------------------------------------------------------------------------------------------
# Fund A's account https://bank.testnet.algorand.network/

# Check A's account balance 
account_info: Dict[str, Any] = algod_client.account_info(addr_A)
print(f"Account balance: {account_info.get('amount')} microAlgos")

# -------------------------------------------------------------------------------------------------
# Create the ASA
# Use the suggested gas fee. 
sp = algod_client.suggested_params()

# Create unsigned transactions 


#   Create ASA asset
txn = transaction.AssetConfigTxn(
    sender=addr_B,
    sp=sp,
    default_frozen=False,
    unit_name= "UCTZAR",
    asset_name= "UCTZAR.",
    manager=addr_B,
    reserve=addr_B,
    freeze=addr_B,
    clawback=addr_B,
    url="",
    total= 10,  
    decimals=0,
)

# Sign with secret key of creator
stxn = txn.sign(pk_B)

# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)

# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")


# Before an account can receive a specific asset it must opt-in to receive it.
# Create opt-in transaction
optin_txn = transaction.AssetOptInTxn(
    sender=addr_A, sp=sp, index=created_asset
)

signed_optin_txn = optin_txn.sign(pk_A)
txid = algod_client.send_transaction(signed_optin_txn)
print(f"Sent opt in transaction with txid: {txid}")

# Wait for the  optin transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# -------------------------------------------------------------------------------------------------
#   A sends 5 Algos to B.
txn_1 = transaction.PaymentTxn(addr_A, sp, addr_B, 500000)

#   B sends 2 Units of UCTZAR to A 
txn_2 = transaction.AssetTransferTxn(
    sender=addr_B,
    sp=sp,
    receiver=addr_A,
    amt=2,
    index=created_asset,
)

# Assign group id to the transactions (order matters!)
transaction.assign_group_id([txn_1, txn_2])

# sign transactions
stxn_1 = txn_1.sign(pk_A)
stxn_2 = txn_2.sign(pk_B)

# combine the signed transactions into a single list (maintain original transaction ordering)
signed_group = [stxn_1, stxn_2]


# -------------------------------------------------------------------------------------------------

# Only the first transaction id is returned
tx_id = algod_client.send_transactions(signed_group)

# wait for confirmation
result: Dict[str, Any] = transaction.wait_for_confirmation(
    algod_client, tx_id, 4
)
print(f"txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")


