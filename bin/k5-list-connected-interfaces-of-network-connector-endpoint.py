#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connector_endpoints/{network connector endpoint id}/interfaces
List Connected Interfaces of Network Connector Endpoint

ネットワークコネクタエンドポイントに接続しているインターフェイスの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-connected-interfaces-of-network-connector-endpoint.py
GET /v2.0/network_connector_endpoints
====================================
port_id
====================================
305485fb-3bff-4230-a1f6-f594ec4ea1fb
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
def access_api(ncep_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id + "/interfaces"

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

  # 接続しているポートの一覧はデータオブジェクトの中の'network_connector_endpoints'キーにオブジェクトとして入っている
  #"data": {
  #  "network_connector_endpoint": {
  #    "interfaces": [
  #      {
  #        "port_id": "305485fb-3bff-4230-a1f6-f594ec4ea1fb"
  #      }
  #    ]
  #  }
  #},
  ncep = data.get('network_connector_endpoint', {})
  interfaces = []

  for item in ncep.get('interfaces', []):
    interfaces.append([item.get('port_id', '')])

  # 一覧を表示
  print("GET /v2.0/network_connector_endpoints/{network connector endpoint id}/interfaces")
  print(tabulate(interfaces, headers=['port_id'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists interfaces which connects to a specified network connector endpoint.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    parser.add_argument('ncep_id', help='network connector endpoint id')
    args = parser.parse_args()
    dump = args.dump
    ncep_id = args.ncep_id

    # 実行
    result = access_api(ncep_id=ncep_id)

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
