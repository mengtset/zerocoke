#!/usr/bin/env python3

import requests
import time
import datetime
import sqlite3


class PriceFetcher(object):

  def __init__(self):
    self.coinstats_url = (
        'https://api.coinstats.app/'
        'public/v1/coins?skip=0&limit=200')
    self.last_success_update_time_isoformat = None
    self.conn = sqlite3.connect('coinstats.db')
    self.cursor = self.conn.cursor()
    self.statistics_table_name = 'statistics'
    self._create_table_if_not_exists(self.statistics_table_name)

  
  def __del__(self):
    self.conn.commit()
    self.conn.close()

  
  def _create_table_if_not_exists(self, table_name):
    for row in self.cursor.execute(
       ('''SELECT name FROM sqlite_master'''
        ''' WHERE type='table' AND name=?'''), (table_name,)):
      return
    self.cursor.execute(
      ('''CREATE TABLE %s '''
       '''(symbol text, time text, name text, price real)''')
       % table_name)
    self.conn.commit()
    print('Table %s created successfully.' % table_name)


  def _refresh(self):
    now_isoformat = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    if now_isoformat == self.last_success_update_time_isoformat:
      return
    response = None
    retries = 3
    while retries > 0:
      try:
        response = requests.get(self.coinstats_url, timeout=2)
        if not response.ok or 'coins' not in response.json():
          retries -= 1
          continue
        break
      except Error:
        retries -= 1
        continue
    print('time = ' + now_isoformat)
    stats = self._parse_response(response)
    for symbol, values in stats.items():
      name, price = values
      self.cursor.execute('''INSERT INTO %s VALUES (?, ?, ?, ?)'''
          % self.statistics_table_name, (symbol, now_isoformat, name, price))
    self.conn.commit()
    self.last_success_update_time_isoformat = now_isoformat


  def _parse_response(self, response):
    stats = {}
    for entry in response.json()['coins']:
      symbol = str(entry['symbol']).upper()
      name = str(entry['name'])
      price = str(entry['price']).upper()
      stats[symbol] = (name, price)
    return stats


  def _iterate_table(self, table_name):
    for row in self.cursor.execute('''SELECT * FROM %s''' % table_name):
      print(row)

if __name__ == '__main__':
  price_fetcher = PriceFetcher()
  while True:
    price_fetcher._refresh()
    # price_fetcher._iterate_table(price_fetcher.statistics_table_name)
    time.sleep(20)

