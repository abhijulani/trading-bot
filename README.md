# Binance Futures Trading Bot (Python)

This project is a Python-based trading bot that places orders on the Binance Futures Testnet.

## Requirements

* Python 3.x
* Binance Testnet account
* API key and secret

## Installation

pip install -r requirements.txt

## Setup

Create a .env file and add your API credentials:

BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

## Run the bot

python bot.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
