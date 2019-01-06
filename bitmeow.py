#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import math
import requests
import time
from wxpy import Bot 


bot = Bot(console_qr=True)
coinstats_url = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=1000'
crypto_stats = {}
synonyms = {}
last_update = 0.0

reply_template = """币种: {} ({})
价格 : ${}
总市值: ${}
市值排名: {}
涨跌
  1小时: {}
  1天    : {}
  1星期: {}
"""


@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  if msg_text in synonyms:
    msg_text = synonyms[msg_text]
  if msg_text not in crypto_stats:
    return
  price = crypto_stats[msg_text]
  msg.chat.send(price)


def refresh_crypto_price():
  response = requests.get(coinstats_url)
  if not response.ok or 'coins' not in response.json():
    return
  for entry in response.json()['coins']:
    symbol = str(entry['symbol']).upper()
    text = crypto_info_formatter(entry)
    crypto_stats[symbol] = text
  last_update = time.time()


def get_synonyms():
  response = requests.get(coinstats_url)
  if not response.ok or 'coins' not in response.json():
    return
  for entry in response.json()['coins']:
    symbol = str(entry['symbol']).upper()
    name = str(entry['name']).upper()
    synonyms[name] = symbol

  # TOP 18 coins' common Chinese names
  synonyms[u'比特币'] = 'BTC'
  synonyms[u'以太坊'] = 'ETH'
  synonyms[u'瑞波币'] = 'XRP'
  synonyms[u'瑞波'] = 'XRP'
  synonyms[u'比特现金'] = 'BCH'
  synonyms[u'柚子'] = 'EOS'
  synonyms[u'恒星币'] = 'XLM'
  synonyms[u'莱特币'] = 'LTC'
  synonyms[u'泰达币'] = 'USDT'
  synonyms[u'波场'] = 'TRX'
  synonyms[u'波场币'] = 'TRX'
  synonyms[u'艾达币'] = 'ADA'
  synonyms[u'卡尔达诺'] = 'ADA'
  synonyms[u'艾欧塔'] = 'MIOTA'
  synonyms[u'埃欧塔'] = 'MIOTA'
  synonyms[u'币安币'] = 'BNB'
  synonyms[u'门罗币'] = 'XMR'
  synonyms[u'达世币'] = 'DASH'
  synonyms[u'新经币'] = 'XEM'
  synonyms[u'以太币'] = 'ETC'
  synonyms[u'以太经典'] = 'ETC'
  synonyms[u'小蚁币'] = 'NEO'
  synonyms[u'小蚁'] = 'NEO'

  # Other interesting coins
  synonyms[u'狗狗币'] = 'DOGE'
  synonyms[u'狗币'] = 'DOGE'
  synonyms[u'火币'] = 'HT'
  synonyms[u'火币积分'] = 'HT'


def crypto_info_formatter(json):
  symbol = json['symbol']
  price = json['price']
  name = json['name']
  rank = json['rank']
  market_cap = json['marketCap']
  priceChange1h = str(json['priceChange1h'])
  priceChange1d = str(json['priceChange1d'])
  priceChange1w = str(json['priceChange1w'])

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
  get_synonyms()
  while True:
    refresh_crypto_price()
    time.sleep(30)
