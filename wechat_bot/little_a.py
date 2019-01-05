#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import requests
from wxpy import *


bot = Bot(console_qr=True)
coinstats_url = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=2000'
crypto_stats = {}
last_update = 0.0

reply_template = """{}
Price : ${}
1H : {}%
24H : {}%
7D: {}%
"""


def refresh_crypto_price():
  response = requests.get(coinstats_url)
  if not response.ok or 'coins' not in response.json():
    return
  for entry in response.json()['coins']:
    symbol = str(entry['symbol']).upper()
    text = crypto_info_formatter(entry)
    crypto_stats[symbol] = text
  last_update = time.time()

@bot.register()
def print_others(msg):
  msg_text = msg.text.strip().upper()
  if msg_text not in crypto_stats:
    return
  if time.time() - last_update > 30.0:
    refresh_crypto_price()
  msg.chat.send(crypto_stats[msg_text])

def crypto_info_formatter(json):
  return reply_template.format(json[u'symbol'], json[u'price'], json[u'priceChange1h'], json[u'priceChange1d'], json[u'priceChange1w'])

if __name__ == '__main__':
  refresh_crypto_price()
  while True:
    time.sleep(100000)
