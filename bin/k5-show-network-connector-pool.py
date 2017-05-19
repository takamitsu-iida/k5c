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
def access_api(nc_pool_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connector_pools/" + nc_pool_id

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

  # ネットワークコネクタプール情報はデータオブジェクトの中の'network_connector_pool'キーにオブジェクトとして入っている
  ncp = data.get('network_connector_pool', {})

  # ネットワーク情報を表示
  nc_pools = []
  nc_pools.append([ncp.get('name', ''), ncp.get('id', '')])
  print("GET /v2.0/network_connector_pools/{network connector pool id}")
  print(tabulate(nc_pools, headers=['name', 'id'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows a specified network connector pool.')
    parser.add_argument('nc_pool_id', metavar='nc-pool-id', help='Network connector pool id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    nc_pool_id = args.nc_pool_id
    dump = args.dump

    # 実行
    result = access_api(nc_pool_id=nc_pool_id)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
