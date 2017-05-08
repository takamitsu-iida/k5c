#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connector_endpoints/{network connector endpoint id}
Show Network Connector Endpoint
ネットワークコネクタエンドポイントの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network-connector-endpoint.py ed44d452-cbc4-4f4c-9c87-03fdf4a7c965
GET /v2.0/network_connector_endpoints/{network connector endpoint id}
====================  =======================================
name                  iida-test-network-connecotor-endpoint-1
id                    ed44d452-cbc4-4f4c-9c87-03fdf4a7c965
endpoint_type         availability_zone
network_connector_id  eceb05fd-8aee-470b-bdca-95f789f181c1
tenant_id             a5001a8b9c4a4712985c11377bd6d4fe
location              jp-east-1a
====================  =======================================
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
def main(ncep_id='', dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id

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

  # ネットワークコネクタエンドポイント情報はデータオブジェクトの中の'network_connector_endpoint'キーにオブジェクトとして入っている
  #"data": {
  #  "network_connector_endpoint": {
  #    "network_connector_id": "eceb05fd-8aee-470b-bdca-95f789f181c1",
  #    "endpoint_type": "availability_zone",
  #    "name": "iida-test-network-connecotor-endpoint-1",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "location": "jp-east-1a",
  #    "id": "ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"
  #  }
  #},
  ncep = data.get('network_connector_endpoint', {})

  # 表示用に配列にする
  nceps = []
  nceps.append(['name', ncep.get('name', '')])
  nceps.append(['id', ncep.get('id', '')])
  nceps.append(['endpoint_type', ncep.get('endpoint_type', '')])
  nceps.append(['network_connector_id', ncep.get('network_connector_id', '')])
  nceps.append(['tenant_id', ncep.get('tenant_id', '')])
  nceps.append(['location', ncep.get('location', '')])

  # ポート情報を表示
  print("GET /v2.0/network_connector_endpoints/{network connector endpoint id}")
  print(tabulate(nceps, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "network_connector_endpoint_id"))
    exit(1)

  main(ncep_id=sys.argv[1], dump=False)
