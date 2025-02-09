import pytest
from send import (
    create_wallet,
    get_stars_address,
    validate_stars_address,
    create_network_config,
    send_ustars
)
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.client import LedgerClient
import os
from dotenv import load_dotenv
import time

# Load environment variables from the .env file
load_dotenv()

def test_address_conversion():
    # Test mnemonic
    mnemonic = os.getenv("MNEMONIC")
    print(f"\nMnemonic being used: {mnemonic}")

    # Create wallet and get address
    wallet = create_wallet(mnemonic)
    stars_address = get_stars_address(wallet)
    print(f"Generated stars address: {stars_address}")

    # Test address validation
    validation_result = validate_stars_address(stars_address)
    print(f"Address validation result: {validation_result}")
    assert validation_result, "Invalid Stargaze address format"
    assert stars_address.startswith("stars"), "Address should start with 'stars'"

    # Test invalid address
    invalid_result1 = validate_stars_address("invalid_address")
    invalid_result2 = validate_stars_address("cosmos1xyz")
    print(f"Invalid address test results: {invalid_result1}, {invalid_result2}")
    assert not invalid_result1
    assert not invalid_result2

def test_network_config():
    config = create_network_config()
    print("\nNetwork Configuration:")
    print(f"Chain ID: {config.chain_id}")
    print(f"URL: {config.url}")
    print(f"Fee denomination: {config.fee_denomination}")
    print(f"Staking denomination: {config.staking_denomination}")
    print(f"Minimum gas price: {config.fee_minimum_gas_price}")

    assert config.chain_id == "elgafar-1"
    assert config.url == "rest+https://rest.elgafar-1.stargaze-apis.com"
    assert config.fee_denomination == "ustars"
    assert config.staking_denomination == "ustars"
    assert config.fee_minimum_gas_price == 1

def test_wallet_creation():
    mnemonic = "view sick wing valley report powder stool napkin whip pluck tunnel cause amused pair inquiry lift various angle tornado wood light mutual grocery pelican"
    wallet = create_wallet(mnemonic)

    print("\nWallet Creation Test:")
    print(f"Wallet object: {wallet}")
    print(f"Wallet address: {wallet.address()}")

    assert wallet is not None
    assert wallet.address() is not None

def test_sign_transaction():
    # Create two test wallets
    sender_mnemonic = os.getenv("MNEMONIC")
    if not sender_mnemonic:
        pytest.skip("No mnemonic provided in environment variables")

    receiver_wallet = LocalWallet.generate()

    # Create sender wallet and get addresses
    sender_wallet = create_wallet(sender_mnemonic)
    sender_address = get_stars_address(sender_wallet)
    receiver_address = get_stars_address(receiver_wallet)

    # Setup network client
    network_config = create_network_config()
    client = LedgerClient(network_config)

    # Get initial balances
    try:
        sender_balance = client.query_bank_balance(sender_address)
        if sender_balance < 2000000:  # Check if we have enough balance for test
            pytest.skip("Insufficient balance in sender wallet")

        receiver_balance = client.query_bank_balance(receiver_address)

        print("\nTransaction Test:")
        print(f"Sender Address: {sender_address}")
        print(f"Sender Initial Balance: {sender_balance}")
        print(f"Receiver Address: {receiver_address}")
        print(f"Receiver Initial Balance: {receiver_balance}")

        # Send 1000000 ustars (1 STARS)
        amount = 1000000
        tx = send_ustars(client, sender_wallet, receiver_address, amount)

        # Wait a bit before checking balances
        time.sleep(5)

        # Get final balances
        final_sender_balance = client.query_bank_balance(sender_address)
        final_receiver_balance = client.query_bank_balance(receiver_address)

        print(f"Transaction hash: {tx.tx_hash}")
        print(f"Sender Final Balance: {final_sender_balance}")
        print(f"Receiver Final Balance: {final_receiver_balance}")

        # Verify the transaction
        assert final_receiver_balance >= receiver_balance + amount, "Receiver didn't receive correct amount"
        assert final_sender_balance <= sender_balance - amount, "Sender balance didn't decrease enough"
        assert tx.tx_hash is not None, "Transaction hash should not be None"

    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        raise



