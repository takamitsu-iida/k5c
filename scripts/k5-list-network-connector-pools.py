#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connector_pools
List Network Connector Pools
ネットワークコネクタプールの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-network-connector-pools.py
GET /v2.0/networks
====================================  ============================
id                                    name
====================================  ============================
e0a80446-203e-4b28-abec-d4b031d5b63e  jp-east-1a_connector_pool_01
====================================  ============================
bash-4.4$
"""

import json
import logging
import os
import sys

# 通常はWARN
# 多めに情報を見たい場合はINFO
logging.basicConfig(level=logging.WARN)

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.error("k5cモジュールのインポートに失敗しました")
  logging.error(e)
  exit(1)

try:
  from k5c import k5config  # need info in k5config.py
except ImportError:
  logging.error("k5configモジュールの読み込みに失敗しました。")
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.error("tabulateモジュールのインポートに失敗しました")
  exit(1)

#
# メイン
#
def main(dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.URL_NETWORK_CONNECTOR_POOLS

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return

  # 戻り値は'status_code'キーに格納
  # ステータスコードが負の場合は、何かおかしかったということ
  if r.get('status_code', -1) < 0:
    logging.error("failed to GET %s", url)
    exit(1)

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    exit(1)

  # ネットワークコネクタプール一覧はデータオブジェクトの中の'network_connector_pools'キーに配列として入っている
  nc_pools_list = []
  for item in data.get('network_connector_pools', []):
    nc_pools_list.append([item.get('id', ''), item.get('name', '')])

  # ネットワークコネクタプール一覧を表示
  print('GET /v2.0/network_connector_pools')
  print(tabulate(nc_pools_list, headers=['id', 'name'], tablefmt='rst'))


if __name__ == '__main__':
  main(dump=False)
