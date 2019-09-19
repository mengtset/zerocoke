#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import time
import wxpy 
import datetime
import sqlite3


bot = wxpy.Bot(console_qr=True)

conn = sqlite3.connect('coinstats.db')
cursor = conn.cursor()

for row in cursor.execute('''SELECT * FROM statistics'''):
  print(row)

statistics_table_name = 'statistics'
one_minute = datetime.timedelta(minutes=1)

@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  if msg_text == 'BTC':
     msg.chat.send('腰斩')

  print(1)
  utc_now = datetime.datetime.utcnow()
  print(2)
  utc_minute_ago = datetime.datetime.utcnow() - one_minute
  print(3)
  now_isoformat = utc_now.strftime('%Y-%m-%d %H:%M')
  print(4)
  minute_ago_isoformat = utc_minute_ago.strftime('%Y-%m-%d %H:%M')
  print(5)

  print(cursor)

  # global cursor


  for row in cursor.execute('''SELECT * FROM statistics'''):
    print(cursor)
    print(row)

  msg.chat.send('$$')

  for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': now_isoformat}):
    print(str(row))
    msg.chat.send(str(row))
    return

  for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': minute_ago_isoformat}):
    print(str(row))
    msg.chat.send(str(row))
    return

  msg.chat.send("X")


while True:
  time.sleep(100000)
