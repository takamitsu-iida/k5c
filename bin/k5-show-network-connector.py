#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connectors/{network connector id}
Show Network Connector
ネットワークコネクタの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network-connector.py eceb05fd-8aee-470b-bdca-95f789f181c1
GET /v2.0/network_connectors/{network connector id}
============================  ====================================  ====================================
name                          id                                    network_connector_pool_id
============================  ====================================  ====================================
iida-test-network-connecotor  eceb05fd-8aee-470b-bdca-95f789f181c1  e0a80446-203e-4b28-abec-d4b031d5b63e
============================  ====================================  ====================================

====================================
network_connector_endpoints
====================================
ed44d452-cbc4-4f4c-9c87-03fdf4a7c965
====================================
"""

import json
import logging
import os
import sys

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
if not here("../lib") in sys.path:
  sys.path.append(here("../lib"))

if not here("../lib/site-packages") in sys.path:
  sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# APIにアクセスする
#
def access_api(network_connector_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connectors/" + network_connector_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  return r


#
# 結果を表示する
#
def print_result(result, dump=False):
  """結果を表示します"""

  # 中身を確認
  if dump:
    print(json.dumps(result, indent=2))
    return

  # ステータスコードは'status_code'キーに格納
  status_code = result.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(result, indent=2))
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # ネットワークコネクタ情報はデータオブジェクトの中の'network_connector'キーにオブジェクトとして入っている
  #"data": {
  #  "network_connector": {
  #    "id": "eceb05fd-8aee-470b-bdca-95f789f181c1",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "network_connector_endpoints": [
  #      "ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"
  #    ],
  #    "network_connector_pool_id": "e0a80446-203e-4b28-abec-d4b031d5b63e",
  #    "name": "iida-test-network-connecotor"
  #  }
  #}
  nc = data.get('network_connector', {})

  # ネットワークコネクタ情報を表示
  ncs = []
  ncs.append([nc.get('name', ''), nc.get('id', ''), nc.get('network_connector_pool_id', '')])
  print("GET /v2.0/network_connectors/{network connector id}")
  print(tabulate(ncs, headers=['name', 'id', 'network_connector_pool_id'], tablefmt='rst'))

  # コネクタエンドポイント一覧を表示
  ncep_list = []
  for item in nc.get('network_connector_endpoints', []):
    ncep_list.append([item])
  print("")
  print(tabulate(ncep_list, headers=['network_connector_endpoints'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows information for a specified network connector.')
    parser.add_argument('network_connector_id', metavar='network-connector-id', help='Network connector id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    network_connector_id = args.network_connector_id
    dump = args.dump

    # 実行
    result = access_api(network_connector_id=network_connector_id)

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
