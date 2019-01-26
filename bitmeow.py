#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import datetime
import math
import pytz
import requests
import time
import wxpy 


COINSTATS_URL = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=2000'
REPLY_TEMPLATE = """币种          {} ({})
价格          ${}
总市值      ${}
市值排名  第{}
涨跌
  1小时      {}
  1天          {}
  1星期      {}
{}
"""

bot = wxpy.Bot(console_qr=True)
symbol2stats = {}
name2symbol = {}
top20_summary_str = ''

# TOP 18 coins' common Chinese names
name2symbol[u'比特币'] = 'BTC'
name2symbol[u'以太坊'] = 'ETH'
name2symbol[u'瑞波币'] = 'XRP'
name2symbol[u'瑞波'] = 'XRP'
name2symbol[u'比特现金'] = 'BCH'
name2symbol[u'柚子'] = 'EOS'
name2symbol[u'恒星币'] = 'XLM'
name2symbol[u'莱特币'] = 'LTC'
name2symbol[u'泰达币'] = 'USDT'
name2symbol[u'波场'] = 'TRX'
name2symbol[u'波场币'] = 'TRX'
name2symbol[u'艾达币'] = 'ADA'
name2symbol[u'卡尔达诺'] = 'ADA'
name2symbol[u'艾欧塔'] = 'MIOTA'
name2symbol[u'埃欧塔'] = 'MIOTA'
name2symbol[u'币安币'] = 'BNB'
name2symbol[u'门罗币'] = 'XMR'
name2symbol[u'达世币'] = 'DASH'
name2symbol[u'新经币'] = 'XEM'
name2symbol[u'以太币'] = 'ETC'
name2symbol[u'以太经典'] = 'ETC'
name2symbol[u'小蚁币'] = 'NEO'
name2symbol[u'小蚁'] = 'NEO'
# Other interesting coins
name2symbol[u'狗狗币'] = 'DOGE'
name2symbol[u'狗币'] = 'DOGE'
name2symbol[u'火币'] = 'HT'
name2symbol[u'火币积分'] = 'HT'
# Common aliases
name2symbol[u'BCHABC'] = 'BCH'
name2symbol[u'BCHSV'] = 'BSV'


@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()

  if '#TOP' in msg_text and top20_summary_str != '':
    msg.chat.send(top20_summary_str)

  for symbol in parse_text_for_symbols(msg_text):
    if symbol in symbol2stats:
      stats = symbol2stats[symbol]
      msg.chat.send(stats)


def parse_text_for_symbols(msg_text):
  result = set()
  # Ignore if the message looks like a URL.
  if 'HTTP://' in msg_text or 'HTTPS://' in msg_text:
    return result

  names_and_symbols = set()
  for piece in msg_text.split('#'):
    longest_match_index = 0
    for i in range(1, len(piece) + 1):
      if piece[:i] in name2symbol.keys() or piece[:i] in name2symbol.values():
        longest_match_index = i
    if longest_match_index > 0:
      names_and_symbols.add(piece[:longest_match_index])
  for name_or_symbol in names_and_symbols:
    if len(name_or_symbol) < 2:
      # Filter out very short symbols like "R", which are very easy
      # to trigger by mistake.
      continue
    if name_or_symbol in name2symbol:
      result.add(name2symbol[name_or_symbol])
    else:
      result.add(name_or_symbol)

  return result



def refresh():
  response = requests.get(COINSTATS_URL)
  if not response.ok or 'coins' not in response.json():
    return
  now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
  yesterday = now - datetime.timedelta(hours=24)
  pretty_now = now.strftime('%Y-%m-%d %H:%M %Z')
  pretty_now_short = now.strftime('%m-%d %H:%M %Z')
  pretty_yesterday_short = yesterday.strftime('%m-%d %H:%M')
  top20_summary = {} 
  for entry in response.json()['coins']:
    symbol = str(entry['symbol']).upper()
    name = str(entry['name']).upper()
    name2symbol[name] = symbol
    symbol2stats[symbol] = stats_formatter(entry, pretty_now)

    rank = entry['rank']
    if rank <= 20:
      price_change_1d = entry['priceChange1d']
      top20_summary[price_change_1d] = '{}      {}      {}'.format( 
                                         symbol, 
                                         prettify_price_change(str(price_change_1d)),
                                         rank)

  global top20_summary_str
  top20_summary_str = (u'前20大币种24小时涨跌排名\n' + '-' * 25 + '\n' + 
                       u'币种      涨跌幅      市值排名\n' +
                       '\n'.join(top20_summary[k] for k in 
                                 sorted(top20_summary.keys(), reverse=True)) + 
                       '\n' + '-' * 25 + '\n' + pretty_yesterday_short +
                       ' ~ ' + pretty_now_short)




def stats_formatter(entry, pretty_now):
  symbol = entry['symbol']
  price = entry['price']
  name = entry['name']
  rank = entry['rank']
  market_cap = entry['marketCap']
  price_change_1h = str(entry['priceChange1h'])
  price_change_1d = str(entry['priceChange1d'])
  price_change_1w = str(entry['priceChange1w'])

  price = prettify_price(price)
  price_change_1h = prettify_price_change(price_change_1h) 
  price_change_1d = prettify_price_change(price_change_1d) 
  price_change_1w = prettify_price_change(price_change_1w) 
  market_cap = prettify_market_cap(market_cap)

  return REPLY_TEMPLATE.format(
                          symbol, 
                          name, 
                          price, 
                          market_cap, 
                          rank, 
                          price_change_1h, 
                          price_change_1d, 
                          price_change_1w,
                          pretty_now)


def prettify_price(price):
  price = str(price)
  accuracy_digits = 6
  parts = price.split('.')
  if len(parts) != 2:
    return price
  int_part, frac_part = parts[0], parts[1]
  if len(int_part) >= accuracy_digits:
    return int_part
  elif int_part != '0':
    remaining_digits = accuracy_digits - len(int_part)
    frac_part = frac_part[:min(len(frac_part), remaining_digits)]
    return int_part + '.' + frac_part
  else:
    non_zeros = str(int(frac_part))
    num_of_zeros = len(frac_part) - len(non_zeros)
    non_zeros = non_zeros[:min(6, len(non_zeros))]
    frac_part = '0' * num_of_zeros + non_zeros
    return int_part + '.' + frac_part


def prettify_price_change(price_change):
  if price_change.startswith('-'):
    return price_change + '%↓'
  else:
    return '+' + price_change + '%↑'


def prettify_market_cap(market_cap):
  market_cap = int(market_cap)
  market_cap_str = str(market_cap)
  digits = len(market_cap_str)

  if (digits <= 4):
    return "不到1万"
  useful = market_cap_str[:4]
  if market_cap >= 10 ** 16:
    return market_cap
  elif market_cap >= 10 ** 12:
    point_pos = digits - 12
    return useful[:point_pos] + '.' + useful[point_pos:] + "万亿"
  elif market_cap >= 10 ** 8:
    point_pos = digits - 8
    return useful[:point_pos] + '.' + useful[point_pos:] + "亿"
  else:
    point_pos = digits - 4
    return useful[:point_pos] + '.' + useful[point_pos:] + "万"


if __name__ == '__main__':
  while True:
    refresh()
    time.sleep(60)

