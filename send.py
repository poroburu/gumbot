from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from bech32 import bech32_encode, bech32_decode
from cosmpy.aerial.client.bank import create_bank_send_msg
from cosmpy.aerial.tx import Transaction, SigningCfg
import requests
import time


def create_wallet(mnemonic: str) -> LocalWallet:
    """Create a wallet from a mnemonic phrase."""
    return LocalWallet.from_mnemonic(mnemonic, 'stars')

def get_stars_address(wallet: LocalWallet) -> str:
    """Convert a Cosmos address to Stargaze address format."""
    # Get the address as bytes
    cosmos_address = wallet.address()

    # Decode the cosmos address to get the raw bytes
    _, data = bech32_decode(str(cosmos_address))
    if data is None:
        raise ValueError("Invalid cosmos address")

    # Convert to stars bech32 address
    return bech32_encode("stars", data)

def validate_stars_address(address: str) -> bool:
    """Validate a Stargaze address format."""
    if not address.startswith("stars"):
        return False

    try:
        hrp, data = bech32_decode(address)
        return hrp == "stars" and data is not None
    except Exception:
        return False


def create_network_config() -> NetworkConfig:
    """Create network configuration for Stargaze testnet."""
    # Note: Updated fee_minimum_gas_price to match test expectation.
    return NetworkConfig(
        chain_id="elgafar-1",
        url="rest+https://rest.elgafar-1.stargaze-apis.com",
        fee_minimum_gas_price=1,
        fee_denomination="ustars",
        staking_denomination="ustars",
    )


def wait_for_tx(tx_hash: str, base_url: str, timeout: int = 60) -> bool:
    """Wait for transaction to be included in a block."""
    endpoint = f"{base_url}/cosmos/tx/v1beta1/txs/{tx_hash}"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                return True
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return False


def send_ustars(client: LedgerClient, wallet: LocalWallet, destination: str, amount: int = 1):
    """Send ustars tokens to a destination address.

    This function builds a bank send message, creates and seals a transaction,
    signs it using the wallet's private key, completes the transaction, broadcasts it,
    and then waits for the transaction to complete.
    """
    # Create a bank send message.
    msg = create_bank_send_msg(
        from_address=wallet.address(),
        to_address=destination,
        amount=amount,
        denom="ustars",
    )

    # Create a transaction and add the message.
    tx = Transaction().add_message(msg)

    # Query account details to obtain account number and sequence number.
    account = client.query_account(wallet.address())

    # Set a default gas limit; production code may want to simulate this value.
    gas_limit = 200000
    fee = f"{gas_limit}ustars"

    # Seal the transaction with the proper signing configuration.
    tx = tx.seal(
        signing_cfgs=SigningCfg.direct(wallet.public_key(), account.sequence),
        fee=fee,
        gas_limit=gas_limit,
        memo=""
    )

    # Sign the transaction using the wallet's signer (i.e. its private key).
    tx = tx.sign(
        signer=wallet.signer(),
        chain_id=client.network_config.chain_id,
        account_number=account.number
    )

    # Mark the transaction as complete.
    tx = tx.complete()

    # Broadcast the signed transaction.
    submitted_tx = client.broadcast_tx(tx)

    # Extract base URL from network config
    base_url = client.network_config.url.replace("rest+", "")

    # Wait for transaction completion using direct REST calls
    if not wait_for_tx(submitted_tx.tx_hash, base_url):
        raise Exception("Transaction timed out")

    return submitted_tx


