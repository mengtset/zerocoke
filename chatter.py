#!/usr/bin/env python3

import wxpy
import redis
import time

cat_ascii = r"""
    /\___/\
   /       \
  l  u   u  l
--l----*----l--
   \   w   /     - Meow!
     ======
   /       \ __
   l        l\ \
   l        l/ /  
   l  l l   l /
   \ ml lm /_/
"""

bot = wxpy.Bot(console_qr=True, cache_path=True)
bot.enable_puid()
r = redis.Redis(host='localhost', port=6379)

bitmeow_puid = '384c167f'
qin_ding_group_puid = '2b6333c6' # 相信光
debug_group_puid = 'c4796f18'
xmsl_puid = 'a6f5c6bd'  # 谢²磨沙驴✘传说割
dalihold_puid = 'a2bd1778'  # 大力hold币
ruguan_puid = 'c5e328d5'  # 入关加速小组
puid_allowed_set = {bitmeow_puid, qin_ding_group_puid, debug_group_puid, xmsl_puid, dalihold_puid, ruguan_puid}

@bot.register()
def respond(msg):
    # print('-' * 20)
    # print('text = ' + msg.text)
    # print('sender.wxid = ' + str(msg.sender.wxid))
    # print('sender.nick_name = ' + str(msg.sender.nick_name))
    print("[SENDER] name = {}, puid = {}".format(msg.sender.name, msg.sender.puid))
    # print('receiver = ' + str(msg.receiver))
    # print('member = ' + str(msg.member))
    # print('type = ' + str(msg.type))
    # print('chat = ' + str(msg.chat))
    # print('-' * 20)

    puid = msg.sender.puid
    if puid not in puid_allowed_set:
        print('Silent in chat with puid = ' + puid)
        return
    symbol = msg.text.strip().upper()
    if symbol == 'MEOW':
        msg.chat.send(cat_ascii)
        return
    if symbol == '涨幅榜':
        msg.chat.send(_get_rank())
        return
    if symbol == '跌幅榜':
        msg.chat.send(_get_rank(reverse=True))
        return

    info = r.hgetall('crypto:'+symbol)
    info = _dict_k_v_to_str(info)
    if not info:
        return
    print('Sending info of ' + symbol + '.')
    msg.chat.send(_format_reply(info))


def _format_reply(info):
    symbol = info.get('symbol')
    name = info.get('name')
    rank = info.get('rank')
    price = info.get('price')
    price = format(float(price), '.9g')

    market_cap = float(info.get('marketCap'))
    if market_cap > 1000000000000.0:
        market_cap = str(format(market_cap / 1000000000000.0, '.2f')) + '万亿'
    elif market_cap > 100000000.0:
        market_cap = str(format(market_cap / 100000000.0, '.2f')) + '亿'
    elif market_cap > 10000.0:
        market_cap = str(format(market_cap / 10000.0, '.2f')) + '万'
    else:
        market_cap = '不到1万'

    change_1h = _add_plus_if_positive(info.get('priceChange1h'))
    change_1d = _add_plus_if_positive(info.get('priceChange1d'))
    change_1w = _add_plus_if_positive(info.get('priceChange1w'))

    result = ('{} ({})   市值第{}\n'.format(symbol, name, rank))
    result += ('价格: US${}\n'.format(price))
    result += ('市值: US${}\n'.format(market_cap))
    result += ('一小时涨跌:{}%\n'.format(change_1h))
    result += ('24小时:{}%  7天:{}%'.format(change_1d, change_1w))

    return result
    
    
def _add_plus_if_positive(percentage):
    percentage = float(percentage)
    if percentage < 0.0:
        return str(percentage)
    return '+' + str(percentage)


def _get_rank(max_rank=50, n_top=10, reverse=False):
    keys = r.keys(pattern='crypto:*')
    keys = [key.decode('utf-8') for key in keys if r.type(key).decode('utf-8') == 'hash']
    dicts = [_dict_k_v_to_str(r.hgetall(name)) for name in keys]
    dicts = [d for d in dicts if int(d.get('rank')) <= max_rank]
    dicts.sort(key=lambda d: float(d.get('priceChange1d')), reverse=(not reverse))
    dicts = dicts[:n_top] 
    report = '-' * 20 + '\n'
    report += '市值前{}品种24小时{}幅榜\n'.format(max_rank, '涨' if reverse is False else '跌')
    report += '-' * 20 + '\n'
    for d in dicts:
        report += '{}: {}%\n'.format(
            d.get('symbol'),
            _add_plus_if_positive(d.get('priceChange1d'))
            )
    return report
    

def _dict_k_v_to_str(info):
    return {k.decode('utf-8') : v.decode('utf-8') for k, v in info.items()}


print(cat_ascii)
bot.join()