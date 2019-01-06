#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import math
import requests
import time
from wxpy import *


bot = Bot(console_qr=True)
coinstats_url = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=2000'
crypto_stats = {}
last_update = 0.0

reply_template = """币种: {} ({})
价格 : ${}
总市值: ${}
市值排名: {}
涨跌
  1小时: {}
  1天   : {}
  1星期: {}
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
  price = crypto_stats[msg_text]
  msg.chat.send(price)


def crypto_info_formatter(json):
  symbol = json[u'symbol']
  name = json[u'name']
  rank = json[u'rank']
  market_cap = json[u'marketCap']
  priceChange1h = str(json['priceChange1h'])
  priceChange1d = str(json['priceChange1d'])
  priceChange1w = str(json['priceChange1w'])

  price = json[u'price']
  price = float(price)
  if price < 1.0 and price > 0.0:
    n_pow = math.ceil(float(-math.log(price, 10)))
    you_xiao_shu_zi = 5
    need_pow = n_pow + you_xiao_shu_zi - 1
    price = int(price * 10 ** need_pow) / float(10 ** need_pow)
  if price >= 1.0:
    trailing = price - int(price)
    trailing = int(trailing * 1000) / 1000.0
    trailing = str(trailing)
    trailing = trailing[1:min(len(trailing), 5)]
    price = str(int(price)) + trailing

  if market_cap >= 100000000:
    market_cap = str(int(market_cap / 100000000)) + "亿"
  elif market_cap >= 10000:
    market_cap = str(int(market_cap / 10000)) + "万"
  else:
    market_cap = "不到1万"
    
  if priceChange1h.startswith('-'):
    priceChange1h += '%↓'
  else:
    priceChange1h = '+' + priceChange1h + '%↑'
    
  if priceChange1d.startswith('-'):
    priceChange1d += '%↓'
  else:
    priceChange1d = '+' + priceChange1d + '%↑'
    
  if priceChange1w.startswith('-'):
    priceChange1w += '%↓'
  else:
    priceChange1w = '+' + priceChange1w + '%↑'

  return reply_template.format(symbol, name, price, market_cap, rank, priceChange1h, priceChange1d, priceChange1w)




if __name__ == '__main__':
  while True:
    refresh_crypto_price()
    time.sleep(30)
