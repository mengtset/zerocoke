#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
from wxpy import Bot 


bot = Bot(console_qr=True)


@bot.register()
def respond(msg):
  msg_text = msg.text.strip().upper()
  msg.chat.send(msg_text)



if __name__ == '__main__':
  while True:
    time.sleep(30)
