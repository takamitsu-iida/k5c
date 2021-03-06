#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/ports/{port_id}
Show port
指定したポートの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-port.py 802c2a2d-5e3e-41c8-8a94-c6430bf48a80
GET /v2.0/ports/{port_id}
=================  ====================================
name               iida-network-1-port-1
id                 802c2a2d-5e3e-41c8-8a94-c6430bf48a80
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         93a83e0e-424e-4e7d-8299-4bdea906354e
binding:vnic_type  normal
mac_address        fa:16:3e:49:02:6d
=================  ====================================

=============  ====================================
ip_address     subnet_id
=============  ====================================
192.168.0.100  38701f66-4610-493f-9c15-78f81917f362
=============  ====================================
bash-4.4$ ]"""

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
def access_api(port_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/ports/" + port_id

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

  # ポート情報はデータオブジェクトの中の'port'キーにオブジェクトとして入っている
  #"data": {
  #  "port": {
  #    "fixed_ips": [
  #      {
  #        "ip_address": "192.168.0.2",
  #        "subnet_id": "8ed6dd7b-2ae3-4f68-81c9-e5d9e074b67a"
  #      }
  #    ],
  #    "extra_dhcp_opts": [],
  #    "mac_address": "fa:16:3e:5e:5d:95",
  #    "admin_state_up": true,
  #    "device_id": "",
  #    "name": "iida-network-1-port-1",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "network_id": "ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #    "status": "DOWN",
  #    "security_groups": [
  #      "783ca685-f16c-497e-a77b-aefcc2fb9127"
  #    ],
  #    "allowed_address_pairs": [],
  #    "availability_zone": "jp-east-1a",
  #    "binding:vnic_type": "normal",
  #    "id": "869ee3b5-9371-41ea-aff5-64dbd214d3b7",
  #    "device_owner": ""
  #  }
  #}
  p = data.get('port', {})

  # 表示用に配列にする
  ports = []
  ports.append(['name', p.get('name', '')])
  ports.append(['id', p.get('id', '')])
  ports.append(['az', p.get('availability_zone', '')])
  ports.append(['tenant_id', p.get('tenant_id', '')])
  ports.append(['status', p.get('status', '')])
  ports.append(['admin_state_up', p.get('admin_state_up', '')])
  ports.append(['device_owner', p.get('device_owner', '')])
  ports.append(['device_id', p.get('device_id', '')])
  ports.append(['network_id', p.get('network_id', '')])
  ports.append(['binding:vnic_type', p.get('binding:vnic_type', '')])
  ports.append(['mac_address', p.get('mac_address', '')])

  # ポート情報を表示
  print("GET /v2.0/ports/{port_id}")
  print(tabulate(ports, tablefmt='rst'))

  # fixed_ipsを表示
  fixed_ips = []
  for item in p.get('fixed_ips', []):
    fixed_ips.append([item.get('ip_address', ''), item.get('subnet_id', '')])
  print("")
  print(tabulate(fixed_ips, headers=['ip_address', 'subnet_id'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows information for a specified port.')
    parser.add_argument('port_id', metavar='port-id', help='Port id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    port_id = args.port_id
    dump = args.dump

    if port_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(port_id=uuid)
          print("port_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(port_id=port_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
