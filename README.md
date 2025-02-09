# Stargaze Discord Dust Bot

A Discord bot that allows users to send small amounts of STARS tokens (dust) on the Stargaze testnet using the CosmPy library.

## Features

- Send dust amounts of STARS tokens via Discord commands
- Validate Stargaze addresses
- Interact with Stargaze testnet
- Full test coverage

## Prerequisites

- Python 3.7+
- Discord Bot Token
- Stargaze Wallet Mnemonic

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install discord.py python-dotenv cosmpy bech32 requests
```

3. Create a `.env` file with:
```
BOT_TOKEN=your_discord_bot_token
MNEMONIC=your_wallet_mnemonic
```


## Usage

The bot responds to the following commands:

- `$hello` - Basic greeting command
- `$dust <address>` - Sends 1 ustars to the specified Stargaze address

## Code Structure

- `example_bot.py` - Main Discord bot implementation and command handling
- `send.py` - Core functionality for Stargaze interactions (wallet creation, transactions)
- `test_send.py` - Comprehensive test suite

## Key Components

### Network Configuration
Uses Stargaze testnet (elgafar-1) with the following configuration:
```rust
    return NetworkConfig(
        chain_id="elgafar-1",
        url="rest+https://rest.elgafar-1.stargaze-apis.com",
        fee_minimum_gas_price=1,
        fee_denomination="ustars",
        staking_denomination="ustars",
    )
```


### Transaction Handling
Implements secure transaction creation, signing and broadcasting using CosmPy's aerial client.

### Address Validation
Includes robust validation for Stargaze addresses to ensure correct formatting and prevent errors.

## Testing


Tests cover:
- Address validation and conversion
- Network configuration
- Wallet creation
- Transaction signing and sending

## Security Notes

- Store sensitive information (bot token, mnemonics) in environment variables
- The bot includes basic validation to prevent malformed transactions
- Uses production-ready libraries for cryptographic operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
