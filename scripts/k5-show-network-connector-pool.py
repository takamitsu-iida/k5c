#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connector_pools/{network connector pool id}
Show Network Connector Pool
ネットワークコネクタプールを表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network-connector-pool.py e0a80446-203e-4b28-abec-d4b031d5b63e
GET /v2.0/network_connector_pools/{network connector pool id}
============================  ====================================
name                          id
============================  ====================================
jp-east-1a_connector_pool_01  e0a80446-203e-4b28-abec-d4b031d5b63e
============================  ====================================
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
def main(nc_pool_id='', dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.URL_NETWORK_CONNECTOR_POOLS + "/" + nc_pool_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return r

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    return r

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    return r

  # ネットワークコネクタプール情報はデータオブジェクトの中の'network_connector_pool'キーにオブジェクトとして入っている
  ncp = data.get('network_connector_pool', {})

  # ネットワーク情報を表示
  nc_pools = []
  nc_pools.append([ncp.get('name', ''), ncp.get('id', '')])
  print("GET /v2.0/network_connector_pools/{network connector pool id}")
  print(tabulate(nc_pools, headers=['name', 'id'], tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "network_connector_pool_id"))
    exit(1)

  main(nc_pool_id=sys.argv[1], dump=False)
