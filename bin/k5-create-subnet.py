#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/subnets
Create subnet
指定したネットワーク上のサブネットを作成する

NOTE:
　・network_idは必須（つまり、先にネットワークを作成しておく必要がある）
　・ip_versionは必須
　・cidrは必須

　・固定IPの場合でもDHCPを使ってアドレスを配布するのでenable_dhcpは常時True
　・DNSサーバはDHCPで配られるので極力設定する
　・同じセグメント上にルータが複数いる場合、仮想サーバにDHCPで経路情報を配布するためhost_routesを設定する
"""

"""
実行例

bash-4.4$ ./k5-create-subnet.py --name iida-az1-subnet03 --network-id 7758033d-5a07-49ef-83e1-25ccdf732cc3 --cidr 10.1.3.0/24
POST /v2.0/subnets
===========  ====================================
name         iida-az1-subnet03
id           f707e1bc-c49c-412d-b2f3-379eb250b6c6
az           jp-east-1a
cidr         10.1.3.0/24
gateway_ip   10.1.3.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   7758033d-5a07-49ef-83e1-25ccdf732cc3
enable_dhcp  True
===========  ====================================
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
def make_request_data(name="", network_id="", cidr="", dns_nameservers=None, az=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  # 作成するサブネットのオブジェクト
  subnet_object = {
    'subnet': {
      'name': name,
      'network_id': network_id,
      'ip_version': 4,  # 常時4
      'cidr': cidr,
      'enable_dhcp': True,  # 常時True
      'availability_zone': az
    }
  }

  # DNSが指定されていたら追加
  if dns_nameservers and len(dns_nameservers) > 0:
    subnet_object['dns_nameservers'] = dns_nameservers

  return subnet_object

#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/subnets"

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

  # 作成したネットワークの情報はデータオブジェクトの中の'subnet'キーにオブジェクトとして入っている
  # "data": {
  #   "subnet": {
  #     "host_routes": [],
  #     "dns_nameservers": [],
  #     "enable_dhcp": true,
  #     "network_id": "ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #     "ip_version": 4,
  #     "name": "iida-subnet-1",
  #     "availability_zone": "jp-east-1a",
  #     "id": "97c0a17a-d062-4869-abde-32e8d426b6ca",
  #     "cidr": "192.168.0.0/24",
  #     "gateway_ip": "192.168.0.1",
  #     "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #     "allocation_pools": [
  #       {
  #         "end": "192.168.0.254",
  #         "start": "192.168.0.2"
  #       }
  #     ]
  #   }
  sn = data.get('subnet', {})

  # 表示用に配列にする
  subnets = []
  subnets.append(['name', sn.get('name', '')])
  subnets.append(['id', sn.get('id', '')])
  subnets.append(['az', sn.get('availability_zone', '')])
  subnets.append(['cidr', sn.get('cidr', '')])
  subnets.append(['gateway_ip', sn.get('gateway_ip', '')])
  subnets.append(['tenant_id', sn.get('tenant_id', '')])
  subnets.append(['network_id', sn.get('network_id', '')])
  subnets.append(['enable_dhcp', sn.get('enable_dhcp', '')])

  # サブネット情報を表示
  print("POST /v2.0/subnets")
  print(tabulate(subnets, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Creates a subnet on a specified network.')
    parser.add_argument('--name', metavar='name', required=True, help='The subnet name.')
    parser.add_argument('--network-id', dest='network_id', metavar='id', required=True, help='The ID of the attached network.')
    parser.add_argument('--cidr', metavar='addr/mask', required=True, help='The CIDR.')
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--dns', nargs='*', default=[], help='DNS server')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    network_id = args.network_id
    cidr = args.cidr
    az = args.az
    dns = args.dns
    dump = args.dump

    # 作成するサブネットの名前
    # name = "iida-az1-net01-subnet01"
    #
    # 所属させるネットワークID
    # network_id = "93a83e0e-424e-4e7d-8299-4bdea906354e"
    #
    # サブネットのアドレス
    # cidr = "192.168.0.0/24"
    #
    # 作成する場所
    # az = "jp-east-1a"
    # az = "jp-east-1b"
    #
    # DNSサーバは環境にあわせて設定する
    # dns = ["133.162.193.9", "133.162.193.10"]  # AZ1の場合
    # dns = ["133.162.201.9", "133.162.201.10"]  # AZ2の場合
    # dns = ["8.8.8.7", "8.8.8.8"]  # GoogleのDNS

    # リクエストデータを作成
    data = make_request_data(name=name, network_id=network_id, cidr=cidr, dns_nameservers=dns, az=az)

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
