# coding=UTF-8

import requests
import json
import pandas
import time
import os


class Djeva():
    _url = 'https://danjuanapp.com/djapi/index_eva/dj'
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'
    }
    _source_dir = 'source'
    _json_dir = 'json'
    _csv_dir = 'csv'

    def __init__(self):
        self.dj = self._fetch()
        self.items = self._items(self.dj)
        self.date = self._date(self.items)

        source_file = os.path.join(self._source_dir, self.date)
        json_file = os.path.join(self._json_dir, self.date)
        csv_file = os.path.join(self._csv_dir, self.date)

        self.source_file = self.dump(
            'json',
            filename=source_file,
            data=self.dj)
        self.json_file = self.dump(
            'json',
            filename=json_file,
            data=self.items)
        self.csv_file = self.dump(
            'csv',
            filename=csv_file,
            data=self.items)

    def dump(self, dtype: str, **kw):
        dump_ops = {
            'json': self._dump_json,
            'csv': self._dump_csv,
        }
        return dump_ops[dtype](**kw)

    def _dump_json(self, filename, data):
        filename = filename + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return filename

    def _dump_csv(self, filename, data):
        filename = filename + '.csv'
        pandas.DataFrame(data).to_csv(filename, index=None)
        return filename

    def _fetch(self):
        return json.loads(requests.get(self._url, headers=self._headers).text)

    def _items(self, dj):
        data = dj['data']
        return data['items']

    def _date(self, items):
        create_time = time.localtime(items[0]['created_at'] // 1000)
        return time.strftime("%Y-%m-%d", create_time)


def main():
    Djeva()


if __name__ == '__main__':
    main()
