# coding=UTF-8

import requests
import json
import pandas
import time
import os

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Djeva():
    _url = 'https://danjuanapp.com/djapi/index_eva/dj'
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'
    }
    _source_dir = 'source'
    _json_dir = 'json'
    _csv_dir = 'csv'
    _csv_columns = [
        'id', 'index_code', 'name', 'ttype', 'pe', 'pb',
        'pe_percentile', 'pb_percentile', 'roe', 'yeild', 'ts',
        'eva_type', 'eva_type_int', 'url', 'bond_yeild', 'begin_at',
        'created_at', 'updated_at', 'pb_flag', 'source', 'date',
        'pb_over_history', 'pe_over_history', 'peg',
    ]
    _min_items = 2
    _required_keys = {
        'id', 'index_code', 'name', 'ttype', 'pe', 'pb',
        'pe_percentile', 'pb_percentile', 'roe', 'yeild', 'ts',
        'eva_type', 'eva_type_int', 'url', 'bond_yeild', 'begin_at',
        'created_at', 'updated_at', 'pb_flag', 'source', 'date',
        'pb_over_history', 'pe_over_history',
    }

    def __init__(self):
        self.dj = self._fetch()
        self.items = self._items(self.dj)
        self._validate(self.items)
        self.date = self._date(self.items)

        if self._is_existing_same(self.date, self.dj, self.items):
            print(f"Data for {self.date} already exists and is unchanged, skipping.")
            return

        source_file = os.path.join(self._source_dir, self.date)
        json_file = os.path.join(self._json_dir, self.date)
        csv_file = os.path.join(self._csv_dir, self.date)
        config_file = 'djeva'

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
        self.dump(
            'config',
            filename=config_file,
            dir=self._source_dir)

    def dump(self, dtype: str, **kw):
        dump_ops = {
            'json': self._dump_json,
            'csv': self._dump_csv,
            'config': self._dump_config,
        }
        return dump_ops[dtype](**kw)

    def _dump_config(self, filename, dir):
        cand_files = os.listdir(dir)
        json_files = [file[:-5]
                      for file in cand_files if file.endswith('json')]
        dates = {}
        for patch in json_files:
            year = patch.split('-')[0]
            month = patch.split('-')[1]
            day = patch.split('-')[2]
            if year not in dates.keys():
                dates[year] = {}
            if month not in dates[year].keys():
                dates[year][month] = []
            dates[year][month].append(day)
            dates[year][month] = sorted(dates[year][month])
        json_files = {'data': dates}
        json_files = 'function get_djeva(){return ' + \
            json.dumps(json_files) + ';}'
        filename = filename + '.js'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_files)
        return filename

    def _dump_json(self, filename, data):
        filename = filename + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return filename

    def _dump_csv(self, filename, data):
        filename = filename + '.csv'
        df = pandas.DataFrame(data)[self._csv_columns]
        df = df.sort_values(by='index_code').reset_index(drop=True)
        df.to_csv(filename, index=None)
        return filename

    def _validate(self, items):
        if not items:
            raise ValueError("fetched items is empty")
        if len(items) < self._min_items:
            raise ValueError(
                f"fetched items count {len(items)} is less than {self._min_items}")
        for idx, item in enumerate(items):
            missing = self._required_keys - set(item.keys())
            if missing:
                raise ValueError(
                    f"item {idx} (id={item.get('id')}) missing keys: {sorted(missing)}")

    def _is_existing_same(self, date, dj, items):
        json_path = os.path.join(self._json_dir, f"{date}.json")
        source_path = os.path.join(self._source_dir, f"{date}.json")
        if not os.path.exists(json_path) or not os.path.exists(source_path):
            return False
        with open(json_path, encoding='utf-8') as f:
            existing_items = json.load(f)
        if not self._items_equal(items, existing_items):
            return False
        with open(source_path, encoding='utf-8') as f:
            existing_source = json.load(f)
        return self._normalize_for_compare(dj) == self._normalize_for_compare(existing_source)

    def _items_equal(self, a, b):
        ignore_keys = {'id', 'created_at', 'updated_at'}
        if len(a) != len(b):
            return False
        a_sorted = sorted(a, key=lambda x: x.get('index_code'))
        b_sorted = sorted(b, key=lambda x: x.get('index_code'))
        for x, y in zip(a_sorted, b_sorted):
            if x.get('index_code') != y.get('index_code'):
                return False
            keys = (set(x.keys()) | set(y.keys())) - ignore_keys
            for k in keys:
                if x.get(k) != y.get(k):
                    return False
        return True

    def _normalize_for_compare(self, obj):
        if isinstance(obj, dict):
            normalized = {k: self._normalize_for_compare(v) for k, v in sorted(obj.items())}
            normalized.pop('id', None)
            normalized.pop('created_at', None)
            normalized.pop('updated_at', None)
            return normalized
        if isinstance(obj, list):
            normalized = [self._normalize_for_compare(x) for x in obj]
            if normalized and all(isinstance(x, dict) and 'index_code' in x for x in normalized):
                normalized.sort(key=lambda x: x['index_code'])
            return normalized
        return obj

    def _fetch(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        resp = session.get(self._url, headers=self._headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

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
