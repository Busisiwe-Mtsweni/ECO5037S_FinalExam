from algosdk import account, mnemonic
from typing import Dict, Any
from algosdk import transaction
from algosdk.v2client import algod

# -----------------------Create two new accounts

# Create a new algod client, configured to connect to a public nodes
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

# Create a function to create accounts


def create_accounts(no_accounts):
    accounts = []

    for _ in range(no_accounts):
        try:
            private_key, address = account.generate_account()
            mnemonic_phrase = mnemonic.from_private_key(private_key)

            accounts.append({
                'mnemonic': mnemonic_phrase
            })
        except Exception as e:
            print(f"An error occurred: {e}")

    return accounts


# Create four new accounts
created_accounts = create_accounts(4)
print(created_accounts)

# Creator  details
mnf = 'picnic enemy join click remain rule depend climb dilemma tattoo old fortune found bachelor float labor exit yard twelve scatter habit degree rally abstract salt'
pkf = mnemonic.to_private_key(mnf)
addrf = account.address_from_private_key(pkf)
print(addrf)

# Store details for user 1
mn1 = 'morning satisfy tortoise input must muscle exist fancy normal fury display scene analyst ethics liquid grant detect ability outside rigid doll october nominee about prize'
pk1 = mnemonic.to_private_key(mn1)
addr1 = account.address_from_private_key(pk1)
print(addr1)


# Store details for user 2
mn2 = 'coconut gorilla rocket antique route possible pizza island involve disagree aspect scan segment timber wreck behind add afraid odor motor silent box artist abstract pass'
pk2 = mnemonic.to_private_key(mn2)
addr2 = account.address_from_private_key(pk2)
print(addr2)


# Store details for user 3
mn3 = 'patch wall apology sail prefer erupt taxi drip jeans letter predict cherry rice youth vicious holiday two govern over sort warfare lumber peace ability label'
pk3 = mnemonic.to_private_key(mn3)
addr3 = account.address_from_private_key(pk3)
print(addr3)

# -----------------------Issue an ASA called fNFT using the creator's details

# Use the suggested gas fee.
sp = algod_client.suggested_params()

# Create unsigned transactions
# Create ASA asset
txn = transaction.AssetConfigTxn(
    sender=addrf,
    sp=sp,
    default_frozen=False,
    unit_name="fNFT",
    asset_name="fNFT",
    manager=addrf,
    reserve=addrf,
    freeze=addrf,
    clawback=addrf,
    url="",
    total=100,
    decimals=1,  # smallest divisible part of each unit is 0.1.
)

# Sign with secret key of creator
stxn = txn.sign(pkf)

# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)

# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")


# -----------------------Create Opt in Transaction using the participants details

addresses = [addr1, addr2, addr3]
pks = [pk1, pk2, pk3]


for addr, pk in zip(addresses, pks):
    # Create an opt-in transaction for each address
    optin_txn = transaction.AssetOptInTxn(
        sender=addr,
        sp=sp,
        index=created_asset
    )

    # Sign the transaction with the corresponding private key
    signed_optin_txn = optin_txn.sign(pk)

    # Send the transaction
    txid = algod_client.send_transaction(signed_optin_txn)
    print(f"Sent opt-in transaction for {addr} with txid: {txid}")

    # Wait for the opt-in transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(
        f"Opt-in confirmed for {addr} in round: {results['confirmed-round']}")

# -----------------------Distribute 1 unit of the fractional NFTs

for addr in addresses:
    txn = transaction.AssetTransferTxn(
        sender=addrf,
        sp=sp,
        receiver=addr,
        amt=1,
        index=created_asset
    )
    # Sign the transaction
    signed_txn = txn.sign(pkf)

    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)

    # Optionally, wait for confirmation and check transaction status
    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")

# -----------------------Check the status of the NFT's


for address in addresses:
    account_info = algod_client.account_info(address)
    assets = account_info.get('assets', [])

    # Check if the account holds the created asset
    held_asset = next(
        (asset for asset in assets if asset['asset-id'] == created_asset), None)

    if held_asset:
        # Display the number of units held
        print(
            f"Address {address} holds {held_asset['amount']} units of fractional NFT (Asset ID: {created_asset})")
    else:
        # Indicate that the asset is not held
        print(
            f"Address {address} does not hold any units of the fractional NFT (Asset ID: {created_asset})")
