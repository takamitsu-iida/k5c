#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/ports
Create port
ポートを作成する

NOTE:
　・親になるネットワークIDが必要
　・同じ名前で何個でも作れる
　・指定しない場合、IPアドレスは自動で割り当てられる
　・指定する場合、サブネットIDが必要
"""

"""
実行例

bash-4.4$ ./bin/k5-create-port.py --name iida-az1-net02-port02 \
--network-id e3c166c0-7e90-4c6e-857e-87fd985f98ac \
--subnet-id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6 \
--ip-address 10.1.2.9

POST /v2.0/ports
=================  ====================================
name               iida-az1-net02-port02
id                 74233502-90d1-47f7-976e-f3def361d2a1
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         e3c166c0-7e90-4c6e-857e-87fd985f98ac
binding:vnic_type  normal
mac_address        fa:16:3e:2a:5a:58
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.2.9      2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
============  ====================================
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
# リクエストデータを作成する
#
def make_request_data(name="", network_id="", subnet_id="", ip_address="", admin_state_up=True, az=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  # 作成するポートのオブジェクト
  port_object = {
    'port': {
      'name': name,
      'network_id': network_id,
      'admin_state_up': admin_state_up,
      'availability_zone': az
    }
  }

  # 固定IPアドレスの指定(配列で指定)
  if ip_address:
    port_object['port']['fixed_ips'] = [{
      'subnet_id': subnet_id,
      'ip_address': ip_address
    }]

  return port_object


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/ports"


  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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

  # 作成したポートの情報はデータオブジェクトの中の'port'キーにオブジェクトとして入っている
  #"data": {
  #  "port": {
  #    "security_groups": [
  #      "783ca685-f16c-497e-a77b-aefcc2fb9127"
  #    ],
  #    "availability_zone": "jp-east-1a",
  #    "allowed_address_pairs": [],
  #    "id": "869ee3b5-9371-41ea-aff5-64dbd214d3b7",
  #    "status": "DOWN",
  #    "fixed_ips": [
  #      {
  #        "ip_address": "192.168.0.2",
  #        "subnet_id": "8ed6dd7b-2ae3-4f68-81c9-e5d9e074b67a"
  #      }
  #    ],
  #    "name": "iida-network-1-port-1",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "admin_state_up": true,
  #    "device_owner": "",
  #    "device_id": "",
  #    "network_id": "ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #    "binding:vnic_type": "normal",
  #    "mac_address": "fa:16:3e:5e:5d:95"
  #  }
  #},
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
  print("POST /v2.0/ports")
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
    parser = argparse.ArgumentParser(description='Creates a port on a specified network.')
    parser.add_argument('--name', metavar='name', required=True, help='The port name.')
    parser.add_argument('--network-id', dest='network_id', metavar='id', required=True, help='The ID of the the network.')
    parser.add_argument('--subnet-id', dest='subnet_id', metavar='id', required=True, help='The ID of the the subnet.')
    parser.add_argument('--ip-address', dest='ip_address', metavar='addr', default='', help='Fixed ip address.')
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()

    name = args.name
    network_id = args.network_id
    subnet_id = args.subnet_id
    ip_address = args.ip_address
    az = args.az
    dump = args.dump

    # 作成するポートの名前
    # name = "iida-network-1-port-1"
    #
    # 所属させるネットワークID
    # network_id = "93a83e0e-424e-4e7d-8299-4bdea906354e"
    #
    # 固定IPを指定する場合に必要
    # そのネットワークに対応付けられるサブネットID
    # subnet_id = "38701f66-4610-493f-9c15-78f81917f362"
    #
    # 固定IPを指定する場合に必要
    # そのサブネットの中からこのポートに割り当てたいIPアドレスを指定する
    # ip_address = "192.168.0.100"
    #
    # 作成する場所
    # az = "jp-east-1a"
    # az = "jp-east-1b"
    #
    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(name=name, network_id=network_id, subnet_id=subnet_id, ip_address=ip_address, az=az)

    # 実行
    result = access_api(data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
