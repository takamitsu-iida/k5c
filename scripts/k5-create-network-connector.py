#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/network_connectors
Create Network Connector
ネットワークコネクタを作成する

NOTE:
　・所属させるネットワークコネクタプールのIDを先に調べる必要がある

bash-4.4$ ./k5-list-network-connector-pools.py
GET /v2.0/network_connector_pools
====================================  ============================
id                                    name
====================================  ============================
e0a80446-203e-4b28-abec-d4b031d5b63e  jp-east-1a_connector_pool_01
====================================  ============================
"""

"""
実行例

bash-4.4$ ./k5-create-network-connector.py
POST /v2.0/network_connectors
=======  ====================================
name     iida-test-network-connecotor
id       385bc7f5-bcc4-4521-ad41-de2074143355
pool_id  e0a80446-203e-4b28-abec-d4b031d5b63e
=======  ====================================
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
# メイン
#
def main(name="", nc_pool_id="", tenant_id="", dump=False):
  """メイン関数"""
  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connectors"

  # 作成するネットワークコネクタのオブジェクト
  nc_object = {
    'network_connector' : {
      'name' : name,
      'network_connector_pool_id' : nc_pool_id,
      'tenant_id' : tenant_id
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=nc_object)

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

  # 作成したネットワークコネクタの情報はdataの中の'network_connector'キーにオブジェクトとして入っている
  nc = data.get('network_connector', {})
  ncs = []
  ncs.append(['name', nc.get('name', '')])
  ncs.append(['id', nc.get('id', '')])
  ncs.append(['pool_id', nc.get('network_connector_pool_id', '')])

  # ネットワークコネクタ情報を表示
  print("POST /v2.0/network_connectors")
  print(tabulate(ncs, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:
      # 作成するネットワークコネクタの名前
      name = "iida-test-network-connecotor"

      # 所属させるネットワークコネクタプールID
      nc_pool_id = "e0a80446-203e-4b28-abec-d4b031d5b63e"

      # 所属させるテナントID
      tenant_id = k5c.TENANT_ID

      # jsonをダンプ
      dump = False

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Create a network connector.')
      parser.add_argument('--name', required=True, help='The network connector name.')
      parser.add_argument('--nc_pool_id', required=True, help='The network connector pool id.')
      parser.add_argument('--tenant_id', default=k5c.TENANT_ID, help='The tenant id.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      name = args.name
      nc_pool_id = args.nc_pool_id
      tenant_id = args.tenant_id
      dump = args.dump

    main(name=name, nc_pool_id=nc_pool_id, tenant_id=tenant_id, dump=dump)

  # 実行
  run_main()
