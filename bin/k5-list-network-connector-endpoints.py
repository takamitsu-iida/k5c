#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connector_endpoints
List Network Connector Endpoints
ネットワークコネクタエンドポイントの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-network-connector-endpoints.py
GET /v2.0/network_connector_endpoints
====================================  =======================================  ====================================
id                                    name                                     network_connector_id
====================================  =======================================  ====================================
f9dec519-8517-4562-91c3-1c09e5eb4c19  iida-test-network-connecotor-endpoint-1  eceb05fd-8aee-470b-bdca-95f789f181c1
====================================  =======================================  ====================================
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
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)


#
# APIにアクセスする
#
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints"

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

  # ネットワークコネクタエンドポイント一覧はデータオブジェクトの中の'network_connector_endpoints'キーに配列として入っている
  #  "data": {
  #    "network_connector_endpoints": [
  #      {
  #        "endpoint_type": "availability_zone",
  #        "network_connector_id": "eceb05fd-8aee-470b-bdca-95f789f181c1",
  #        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #        "id": "f9dec519-8517-4562-91c3-1c09e5eb4c19",
  #        "name": "iida-test-network-connecotor-endpoint-1",
  #        "location": "jp-east-1a"
  #      }
  #    ]
  #  },
  ncep_list = []
  for item in data.get('network_connector_endpoints', []):
    ncep_list.append([item.get('id', ''), item.get('name', ''), item.get('network_connector_id', '')])

  # 一覧を表示
  print("GET /v2.0/network_connector_endpoints")
  print(tabulate(ncep_list, headers=['id', 'name', 'network_connector_id'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List network connector endpoints.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 得たデータを処理する
    print_result(result, dump=dump)

  # 実行
  main()
