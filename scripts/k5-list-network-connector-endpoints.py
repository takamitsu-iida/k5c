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
  url = k5config.URL_NETWORK_CONNECTOR_ENDPOINTS

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

  # 結果を返す
  return r


if __name__ == '__main__':
  main(dump=False)
