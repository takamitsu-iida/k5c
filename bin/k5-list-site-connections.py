#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/ipsec-site-connections
List IPSec site connections
IPsecのサイト間の接続を一覧表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-site-connections.py
GET /v2.0/vpn/ipsec-site-connections
====================================  ======================  ==============  ========  ===================
id                                    name                    peer_address    status    availability_zone
====================================  ======================  ==============  ========  ===================
4273f817-da1c-4aa5-9445-6501d5bed29d  iida-az1-connection-01  2.2.2.2         DOWN      jp-east-1a
====================================  ======================  ==============  ========  ===================
bash-4.4$
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
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsec-site-connections"

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

  #{
  #  "status_code": 200,
  #  "data": {
  #    "ipsec_site_connections": [
  #      {
  #        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #        "ikepolicy_id": "9fc16042-95ae-46b9-84bc-4777b3b9f89c",
  #        "auth_mode": "psk",
  #        "id": "5633040d-b30d-476c-9104-a0ee4c28d298",
  #        "peer_cidrs": [
  #          "10.1.1.0/24"
  #        ],
  #        "vpnservice_id": "75f35f53-ecbd-4748-a070-3316435e35cc",
  #        "status": "DOWN",
  #        "dpd": {
  #          "interval": 10,
  #          "timeout": 30,
  #          "action": "restart"
  #        },
  #        "description": "",
  #        "ipsecpolicy_id": "26525271-0337-4ad2-b0d3-120814fc0794",
  #        "psk": "passpass",
  #        "route_mode": "static",
  #        "peer_address": "1.1.1.1",
  #        "mtu": 1500,
  #        "admin_state_up": true,
  #        "availability_zone": "jp-east-1a",
  #        "peer_id": "@x.x.x.x",
  #        "name": "iida-az1-connection-01",
  #        "initiator": "bi-directional"
  #      },

  disp_keys = ['id', 'name', 'peer_address', 'status', 'availability_zone']

  disp_list = []
  for item in data.get('ipsec_site_connections', []):
    row = []
    for key in disp_keys:
      row.append(item.get(key, ''))
    disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/vpn/ipsec-site-connections")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists the IPSec site-to-site connections.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
