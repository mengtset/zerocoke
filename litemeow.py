#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import time
import wxpy 


bot = wxpy.Bot(console_qr=True)


@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  if msg_text == 'BTC':
     msg.chat.send('腰斩')

while True:
  time.sleep(100000)
