#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/ipsec-site-connections/{connection-id}
Show IPSec site connection details
指定したIPsecサイト間の接続の詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-site-connections.py | ./bin/k5-show-site-connection.py -
connection_id: d2a3ddf3-3b0c-4914-8851-17cd0eece29e
GET /v2.0/vpn/ipsec-site-connections/{connection-id}
=================  ====================================
name               iida-az1-connection-01
id                 d2a3ddf3-3b0c-4914-8851-17cd0eece29e
peer_address       2.2.2.2
peer_id            2.2.2.2
psk                passpass
vpnservice_id      75f35f53-ecbd-4748-a070-3316435e35cc
ikepolicy_id       9fc16042-95ae-46b9-84bc-4777b3b9f89c
ipsecpolicy_id     26525271-0337-4ad2-b0d3-120814fc0794
route_mode         static
mtu                1500
initiator          bi-directional
auth_mode          psk
status             DOWN
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
availability_zone  jp-east-1a
description
=================  ====================================
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
def access_api(connection_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsec-site-connections/" + connection_id

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
  #  "data": {
  #    "ipsec_site_connection": {
  #      "dpd": {
  #        "action": "restart",
  #        "timeout": 30,
  #        "interval": 10
  #      },
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "admin_state_up": true,
  #      "description": "",
  #      "initiator": "bi-directional",
  #      "ipsecpolicy_id": "26525271-0337-4ad2-b0d3-120814fc0794",
  #      "name": "iida-az1-connection-01",
  #      "route_mode": "static",
  #      "peer_cidrs": [
  #        "10.2.1.0/24"
  #      ],
  #      "psk": "passpass",
  #      "auth_mode": "psk",
  #      "status": "DOWN",
  #      "mtu": 1500,
  #      "peer_address": "2.2.2.2",
  #      "peer_id": "2.2.2.2",
  #      "id": "d2a3ddf3-3b0c-4914-8851-17cd0eece29e",
  #      "ikepolicy_id": "9fc16042-95ae-46b9-84bc-4777b3b9f89c",
  #      "vpnservice_id": "75f35f53-ecbd-4748-a070-3316435e35cc",
  #      "availability_zone": "jp-east-1a"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 200
  #}

  item = data.get('ipsec_site_connection', {})

  disp_keys = [
    'name', 'id', 'peer_address', 'peer_id', 'psk',
    'vpnservice_id', 'ikepolicy_id', 'ipsecpolicy_id',
    'route_mode', 'mtu', 'initiator', 'auth_mode', 'status',
    'tenant_id', 'availability_zone', 'description']

  disp_list = []

  for key in disp_keys:
    row = []
    row.append(key)
    row.append(item.get(key, ''))
    disp_list.append(row)

  print("GET /v2.0/vpn/ipsec-site-connections/{connection-id}")
  print(tabulate(disp_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows details about a specified IPSec site-to-site connection.')
    parser.add_argument('connection_id', metavar='id', help='The vpnservice id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    connection_id = args.connection_id
    dump = args.dump

    if connection_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(connection_id=uuid)
          print("connection_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(connection_id=connection_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
