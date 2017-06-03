#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/networks/{network_id}
Show network
指定したネットワークの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network.py 93a83e0e-424e-4e7d-8299-4bdea906354e
GET /v2.0/networks/{network_id}
===================  ====================================  ==========  ========
name                 id                                    az          status
===================  ====================================  ==========  ========
iida-test-network-1  93a83e0e-424e-4e7d-8299-4bdea906354e  jp-east-1a  ACTIVE
===================  ====================================  ==========  ========

====================================
subnet
====================================
38701f66-4610-493f-9c15-78f81917f362
====================================
"""

import json
import logging
import os
import sys

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  if getattr(sys, 'frozen', False):
    # cx_Freezeで固めた場合は実行ファイルからの相対パス
    return os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
  else:
    # 通常はこのファイルの場所からの相対パス
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
def access_api(network_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/networks/" + network_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  return r


#
# 結果を表示する
#
def print_result(result):
  """結果を表示します"""

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

  # ネットワーク情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 200,
  #  "data": {
  #    "network": {
  #      "id": "8f15da62-c7e5-47ec-8668-ee502f6d00d2",
  #      "router:external": false,
  #      "availability_zone": "jp-east-1a",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "admin_state_up": true,
  #      "status": "ACTIVE",
  #      "subnets": [
  #        "abbbbcf4-ea8f-4218-bbe7-669231eeba30"
  #      ],
  #      "shared": false,
  #      "name": "iida-az1-net01"
  #    }
  #  }
  #}

  nw = data.get('network', {})

  # ネットワーク情報を表示
  networks = []
  networks.append([nw.get('name', ''), nw.get('id', ''), nw.get('availability_zone', ''), nw.get('status', '')])
  print("GET /v2.0/networks/{network_id}")
  print(tabulate(networks, headers=['name', 'id', 'az', 'status'], tablefmt='rst'))

  # サブネット一覧を表示
  subnets_list = []
  for item in nw.get('subnets', []):
    subnets_list.append([item])
  print("")
  print(tabulate(subnets_list, headers=['subnet'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows information for a specified network.')
    parser.add_argument('network_id', metavar='id', help='The UUID of the network id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    network_id = args.network_id
    dump = args.dump

    if network_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(network_id=uuid)
          print("network_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(network_id=network_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
