#!/usr/bin/env python3

import datetime
import redis
import requests
import time

COINSTATS_URL = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=2000'

class Fetcher(object):

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379)
        

    def _refresh(self):
        # Coinstats server will return same 'cached' result if same URL is used during
        # a short interval, append timestamp as a junk value to deceive the server.
        timetag = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        url = COINSTATS_URL + '&tag=' + timetag 
        response = requests.get(url)
        if not response.ok or 'coins' not in response.json():
            print('[FAIL] ' + timetag)
            return False
        try:
            stats = self._parse_response(response)
        except:
            print('[FAIL] ' + timetag)
            return False
        for symbol, data in stats.items():
            # Append fetching timestamp for reference.
            data['timestamp'] = timetag
            symbol = 'crypto:'+symbol
            self.r.hset(name=symbol, mapping=data)
            self.r.expire(name=symbol, time=datetime.timedelta(seconds=60))
        print('[OK] ' + timetag)
        return True
        

    def _parse_response(self, response):
        stats = {}
        for entry in response.json()['coins']:
            symbol = str(entry['symbol']).upper()
            # Cast dict key and value to string for redis storage.
            stats[symbol] = {str(key) : str(val) for key, val in entry.items()}
        return stats

if __name__ == '__main__':
    fetcher = Fetcher()
    while True:
        fetcher._refresh()
        time.sleep(5)
