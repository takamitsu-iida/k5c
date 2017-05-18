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

bash-4.4$ ./bin/k5-create-network-connector-endpoint.py \
--name iida-az1-ncep2 \
--nc-id 48b97e90-f215-483d-80cd-1854d168aa6d

POST /v2.0/network_connector_endpoints
=============  ====================================
name           iida-az1-ncep2
id             31b72eba-f471-408d-a9da-3bb317b01b1b
nc_id          48b97e90-f215-483d-80cd-1854d168aa6d
tenant_id      a5001a8b9c4a4712985c11377bd6d4fe
location       jp-east-1a
endpoint_type  availability_zone
=============  ====================================
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
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)


#
# リクエストデータを作成する
#
def make_request_data(name="", nc_id="", az="", endpoint_type="", tenant_id=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

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

  return ncep_object


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Create a network connector endpoint.')
    parser.add_argument('--name', metavar='name', required=True, help='The network connector endpoint name.')
    parser.add_argument('--nc-id', dest='nc_id', metavar='id', required=True, help='The network connector id.')
    parser.add_argument('--az', nargs='?', default='jp-east-1a', help='The availability zone. default: jp-east-1a')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    nc_id = args.nc_id
    az = args.az
    dump = args.dump

    # 作成するネットワークコネクタエンドポイントの名前
    # name = "iida-test-network-connecotor-endpoint-1"
    #
    # 所属させるネットワークコネクタID
    # nc_id = "eceb05fd-8aee-470b-bdca-95f789f181c1"
    #
    # エンドポイントタイプ
    # "availability_zone" or "remote"
    # ここではazで固定
    # endpoint_type = "availability_zone"
    #
    # ロケーション
    # エンドポイントタイプがavailability_zoneの場合はその名前
    # az = "jp-east-1a"  # or "jp-east-1b"
    #
    # 所属させるテナントID
    # tenant_id = k5c.TENANT_ID
    #
    # jsonをダンプ
    # dump = False

    # エンドポイントタイプ "availability_zone" or "remote"
    endpoint_type = "availability_zone"

    # 所属させるテナントID
    tenant_id = k5c.TENANT_ID

    # リクエストデータを作成
    data = make_request_data(name=name, nc_id=nc_id, az=az, endpoint_type=endpoint_type, tenant_id=tenant_id)

    # 実行
    result = access_api(data=data)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
