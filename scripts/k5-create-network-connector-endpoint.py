#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/network_connector_endpoints
Create Network Connector Endpoint
ネットワークコネクタエンドポイントを作成する

注意：
　・コネクタエンドポイントを作るには、先に所属させるネットワークコネクタが存在しなければいけない
　・IDを調べるにはk5-list-network-connectors.pyを使う

bash-4.4$ ./k5-list-network-connectors.py
GET /v2.0/network_connectors
====================================  ============================  ====================================  ================================
id                                    name                          pool_id                               tenant_id
====================================  ============================  ====================================  ================================
eceb05fd-8aee-470b-bdca-95f789f181c1  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
====================================  ============================  ====================================  ================================
"""

"""
実行例
bash-4.4$ ./k5-create-network-connector-endpoint.py
POST /v2.0/network_connector_endpoints
=============  =======================================
name           iida-test-network-connecotor-endpoint-1
id             ed44d452-cbc4-4f4c-9c87-03fdf4a7c965
nc_id          eceb05fd-8aee-470b-bdca-95f789f181c1
tenant_id      a5001a8b9c4a4712985c11377bd6d4fe
location       jp-east-1a
endpoint_type  availability_zone
=============  =======================================

実行例（作成失敗の場合）
bash-4.4$ ./k5-create-network-connector-endpoint.py
{
  "Content-Type": "application/json;charset=utf-8",
  "status_code": 409,
  "data": {
    "NeutronError": {
      "type": "EndpointAlreadyExist",
      "detail": "network connector id: eceb05fd-8aee-470b-bdca-95f789f181c1, type: availability_zone, location: jp-east-1a",
      "message": "network connector endpoint already exist"
    },
    "request_id": "a79772bc-a08c-40b9-ae52-922857e29ff6"
  }
}
"""

import json
import logging
import os
import sys

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  exit(1)

try:
  from k5c import k5config  # need info in k5config.py
except ImportError as e:
  logging.exception("k5configモジュールの読み込みに失敗しました: %s", e)
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(name="", nc_id="", endpoint_type="availability_zone", az="", tenant_id="", dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/network_connector_endpoints"

  # 作成するネットワークコネクタエンドポイントのオブジェクト
  ncep_object = {
    'network_connector_endpoint' : {
      'name': name,
      'network_connector_id': nc_id,
      'endpoint_type': endpoint_type,
      "location" : az,
      'tenant_id' : tenant_id
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=ncep_object)

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

  # 作成したネットワークコネクタエンドポイントの情報はdataの中の'network_connector_endpoint'キーにオブジェクトとして入っている
  # "data": {
  #   "network_connector_endpoint": {
  #     "id": "fa81d11c-fbe1-4b36-8ef3-5b8c0a93a2fd",
  #     "name": "iida-test-network-connecotor-endpoint-1",
  #     "network_connector_id": "eceb05fd-8aee-470b-bdca-95f789f181c1",
  #     "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #     "location": "jp-east-1a",
  #     "endpoint_type": "availability_zone"
  #   }
  # },
  ncep = data.get('network_connector_endpoint', {})

  # 表示用に配列に変換する
  nceps = []
  nceps.append(['name', ncep.get('name', '')])
  nceps.append(['id', ncep.get('id', '')])
  nceps.append(['nc_id', ncep.get('network_connector_id', '')])
  nceps.append(['tenant_id', ncep.get('tenant_id', '')])
  nceps.append(['location', ncep.get('location', '')])
  nceps.append(['endpoint_type', ncep.get('endpoint_type', '')])

  # ネットワークコネクタ情報を表示
  print("POST /v2.0/network_connector_endpoints")
  print(tabulate(nceps, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:
      # 作成するネットワークコネクタエンドポイントの名前
      name = "iida-test-network-connecotor-endpoint-1"

      # 所属させるネットワークコネクタID
      nc_id = "eceb05fd-8aee-470b-bdca-95f789f181c1"

      # エンドポイントタイプ
      # "availability_zone" or "remote"
      # ここではazで固定
      endpoint_type = "availability_zone"

      # ロケーション
      # エンドポイントタイプがavailability_zoneの場合はその名前
      az = "jp-east-1a"  # or "jp-east-1b"

      # 所属させるテナントID
      tenant_id = k5config.TENANT_ID

      # jsonをダンプ
      dump = False

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Create a network connector endpoint.')
      parser.add_argument('--name', required=True, help='The network connector endpoint name.')
      parser.add_argument('--nc_id', required=True, help='The network connector id.')
      parser.add_argument('--az', required=True, help='The availability zone.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      name = args.name
      nc_id = args.nc_id
      az = args.az
      dump = args.dump

      # エンドポイントタイプ "availability_zone" or "remote"
      endpoint_type = "availability_zone"

      # 所属させるテナントID
      tenant_id = k5config.TENANT_ID

    main(name=name, nc_id=nc_id, az=az, endpoint_type=endpoint_type, tenant_id=tenant_id, dump=dump)

  # 実行
  run_main()
