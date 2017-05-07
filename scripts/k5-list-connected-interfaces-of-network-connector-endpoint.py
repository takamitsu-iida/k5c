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
def main(ncep_id, dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.URL_NETWORK_CONNECTOR_ENDPOINTS + "/" + ncep_id + "/interfaces"

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

  # 結果を返す
  return r


if __name__ == '__main__':

  # 対象のコネクタエンドポイントID
  # ncep_id="ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"

  main(ncep_id="ed44d452-cbc4-4f4c-9c87-03fdf4a7c965", dump=False)
