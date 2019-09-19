#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import time
import wxpy 
import datetime
import sqlite3


bot = wxpy.Bot(console_qr=True)

@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  utc_now = datetime.datetime.utcnow()
  utc_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
  now_isoformat = utc_now.strftime('%Y-%m-%d %H:%M')
  minute_ago_isoformat = utc_minute_ago.strftime('%Y-%m-%d %H:%M')
  conn = sqlite3.connect('coinstats.db')
  cursor = conn.cursor()
  for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': now_isoformat}):
    print(type(row))
    msg.chat.send(row)
    return
  for row in cursor.execute('''SELECT * FROM statistics WHERE symbol=:symbol AND time=:time''', {'symbol': msg_text, 'time': now_isoformat}):
    msg.chat.send(row)
    return
  cursor.close()
  conn.close()



bot.join()



