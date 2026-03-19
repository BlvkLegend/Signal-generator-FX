import os
import time
from tvDatafeed import TvDatafeed, Interval
import requests
import pandas as pd
import ta

class TradeSignal:
    def __init__(self, symbol, signal_type, price):
        self.symbol = symbol
        self.signal_type = signal_type  # 'buy' or 'sell'
        self.price = price

    def __repr__(self):
        return f'TradeSignal(symbol={self.symbol}, signal_type={self.signal_type}, price={self.price})'

def fetch_forex_data(symbol):
    tv = TvDatafeed(username='your_username', password='your_password')  # Replace with your actual credentials
    data = tv.get_hist(symbol, interval=Interval.in_15_minute, n_bars=500)
    return data

def calculate_indicators(data):
    data['SMA_14'] = data['close'].rolling(window=14).mean()
    data['RSI'] = ta.momentum.rsi(data['close'], window=14)
    return data

def generate_signals(data):
    signals = []
    for i in range(1, len(data)):
        if data['close'].iloc[i] > data['SMA_14'].iloc[i] and data['close'].iloc[i-1] <= data['SMA_14'].iloc[i-1]:
            signals.append(TradeSignal(symbol='EUR/USD', signal_type='buy', price=data['close'].iloc[i]))
        elif data['close'].iloc[i] < data['SMA_14'].iloc[i] and data['close'].iloc[i-1] >= data['SMA_14'].iloc[i-1]:
            signals.append(TradeSignal(symbol='EUR/USD', signal_type='sell', price=data['close'].iloc[i]))
    return signals

def send_telegram_message(message):
    telegram_key = os.getenv('TELEGRAM_KEY')
    telegram_chat = os.getenv('TELEGRAM_CHAT')
    url = f'https://api.telegram.org/bot{telegram_key}/sendMessage'
    payload = {
        'chat_id': telegram_chat,
        'text': message
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    while True:
        forex_data = fetch_forex_data('EURUSD')  # Change the symbol as needed
        processed_data = calculate_indicators(forex_data)
        trade_signals = generate_signals(processed_data)
        for signal in trade_signals:
            message = f'Signal: {signal.signal_type} for {signal.symbol} at {signal.price}'
            send_telegram_message(message)
        time.sleep(900)  # Sleep for 15 minutes before the next fetch
