# ────────────────────────────────────────────────
#    Forex Signal Generator with Telegram Integration
# ────────────────────────────────────────────────

import requests
import pandas as pd
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval
import json

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    config = {
        'telegram_api_key': '7738815469:AAGZ9CinWjcfp5ntRGiludabkRHRRgdnwiM',
        'chat_id': '942718846',
        'forex_pairs': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF']
    }

TELEGRAM_KEY = config['telegram_api_key']
TELEGRAM_CHAT = config['chat_id']
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage"
FOREX_PAIRS = config['forex_pairs']

class TradeSignal:
    def __init__(self, pair, direction, entry, sl, tp):
        self.pair = pair
        self.direction = direction
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    def to_telegram_format(self):
        return f"🎯 {self.pair} | {self.direction} | Entry: {self.entry:.5f} | SL: {self.sl:.5f} | TP: {self.tp:.5f} | {self.timestamp}"

def fetch_candles(pair):
    try:
        tv = TvDatafeed()
        df = tv.get_hist(pair, 'FX', Interval.in_15_minute, n_bars=500)
        return df
    except Exception as e:
        print(f"Error fetching {pair}: {e}")
        return None

def generate_signal(pair, df):
    if df is None or len(df) < 60:
        return None
    
    try:
        recent = df.iloc[-1]
        highs = df['high'].iloc[-22:-2]
        lows = df['low'].iloc[-22:-2]
        range_high = highs.max()
        range_low = lows.min()
        pip_size = 0.01 if 'JPY' in pair else 0.0001
        
        if recent['high'] > range_high and recent['close'] < range_high:
            return TradeSignal(pair, 'SELL', recent['close'], 
                             recent['close'] + (10 * pip_size), 
                             recent['close'] - (30 * pip_size))
        elif recent['low'] < range_low and recent['close'] > range_low:
            return TradeSignal(pair, 'BUY', recent['close'], 
                             recent['close'] - (10 * pip_size), 
                             recent['close'] + (30 * pip_size))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_telegram_signal(signal):
    try:
        payload = {"chat_id": TELEGRAM_CHAT, "text": signal.to_telegram_format()}
        requests.post(TELEGRAM_URL, json=payload, timeout=10)
        return True
    except:
        return False

if __name__ == '__main__':
    print("🚀 Forex Signal Generator Started")
    for pair in FOREX_PAIRS:
        df = fetch_candles(pair)
        signal = generate_signal(pair, df)
        if signal:
            send_telegram_signal(signal)
            print(f"✅ {pair}: {signal.direction}")
