#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import time
import wxpy 
import datetime
import sqlite3
import threading

bot = wxpy.Bot(console_qr=True)
lock = threading.Lock()
active_symbols = []


@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  with lock:
    if msg_text not in active_symbols:
      return
  conn = sqlite3.connect('coinstats.db')
  cursor = conn.cursor()
  now, minute_ago = get_now_and_ago()
  latest = None
  for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': now}):
    latest = row
    break
  if latest is None:
    for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': minute_ago}):
      latest = row
      break
  cursor.close()
  conn.close()
  if latest is None:
    return
  symbol, time, name, price = latest
  # time += ' UTC'
  price = '${:6.5f}'.format(price)
  if symbol != name:
    msg.chat.send('{} ({})\n{}'.format(symbol, name, price))
  else:
    msg.chat.send('{}\n{}'.format(symbol, price))


def get_now_and_ago():
  utc_now = datetime.datetime.utcnow()
  utc_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
  now_isoformat = utc_now.strftime('%Y-%m-%d %H:%M')
  minute_ago_isoformat = utc_minute_ago.strftime('%Y-%m-%d %H:%M')
  return now_isoformat, minute_ago_isoformat


while True:
  conn = sqlite3.connect('coinstats.db')
  cursor = conn.cursor()
  now, minute_ago = get_now_and_ago()
  new_active_symbols = []
  for row in cursor.execute('''SELECT DISTINCT symbol FROM statistics WHERE time=?''', (now, )):
    new_active_symbols.append(row[0])
  for row in cursor.execute('''SELECT DISTINCT symbol FROM statistics WHERE time=?''', (minute_ago, )):
    new_active_symbols.append(row[0])
  with lock:
    active_symbols = new_active_symbols
  time.sleep(60)

