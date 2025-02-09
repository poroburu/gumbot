import os
from dotenv import load_dotenv
import discord
from send import (
    create_wallet,
    validate_stars_address,
    create_network_config,
    send_ustars
)
from cosmpy.aerial.client import LedgerClient

# Load environment variables from the .env file
load_dotenv()

# Retrieve the bot token and mnemonic from the environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
MNEMONIC = os.getenv("MNEMONIC")

if BOT_TOKEN is None or MNEMONIC is None:
    raise ValueError("BOT_TOKEN or MNEMONIC not found in environment variables. Please set them in the .env file.")

# Set up Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Set up Stargaze client and wallet
network_config = create_network_config()
ledger_client = LedgerClient(network_config)
wallet = create_wallet(MNEMONIC)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    elif message.content.startswith('$dust'):
        # Split the message to get the address
        try:
            _, address = message.content.split(maxsplit=1)
            address = address.strip()

            # Validate the address
            if not validate_stars_address(address):
                await message.channel.send('Invalid Stargaze address! Address should start with "stars".')
                return

            # Send 1 ustars
            try:
                await message.channel.send(f'Sending 1 ustars to {address}...')
                tx = send_ustars(ledger_client, wallet, address, 1)
                await message.channel.send(f'Successfully sent 1 ustars! Transaction hash: {tx.tx_hash}')
            except Exception as e:
                await message.channel.send(f'Failed to send ustars: {str(e)}')

        except ValueError:
            await message.channel.send('Please provide a valid Stargaze address. Usage: $dust <address>')

client.run(BOT_TOKEN)
