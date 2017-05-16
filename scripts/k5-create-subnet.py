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

ネットワークIDを調べる
bash-4.4$ ./k5-list-networks.py
GET /v2.0/networks
====================================  ===================  ================================  ==========  ========
id                                    name                 tenant_id                         az          status
====================================  ===================  ================================  ==========  ========
93a83e0e-424e-4e7d-8299-4bdea906354e  iida-test-network-1  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE

このネットワークIDに対応付けるサブネットを作成する。

bash-4.4$ ./k5-create-subnet.py
POST /v2.0/subnets
===========  ====================================
name         iida-subnet-1
id           38701f66-4610-493f-9c15-78f81917f362
az           jp-east-1a
cidr         192.168.0.0/24
gateway_ip   192.168.0.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   93a83e0e-424e-4e7d-8299-4bdea906354e
enable_dhcp  True
===========  ====================================
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
def main(name="", network_id="", ip_version=4, cidr="", az="", dns_nameservers=None, dump=False):
  """メイン関数"""
  # pylint: disable=too-many-arguments

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/subnets"

  # 作成するサブネットのオブジェクト
  subnet_object = {
    'subnet': {
      'name': name,
      'network_id': network_id,
      'ip_version': ip_version,
      'cidr': cidr,
      'enable_dhcp': True,  # 常時True
      'availability_zone': az
    }
  }

  # DNSが指定されていたら追加
  if dns_nameservers and len(dns_nameservers) > 0:
    subnet_object['dns_nameservers'] = dns_nameservers

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=subnet_object)

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

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:
      # 作成するサブネットの名前
      name = "iida-subnet-1"

      # 所属させるネットワークID
      network_id = "93a83e0e-424e-4e7d-8299-4bdea906354e"

      # サブネットのアドレス
      cidr = "192.168.0.0/24"

      # 作成する場所
      az = "jp-east-1a"
      # az = "jp-east-1b"

      # DNSサーバは環境にあわせて設定する
      dns = ["133.162.193.9", "133.162.193.10"]  # AZ1の場合
      # dns = ["133.162.201.9", "133.162.201.10"]  # AZ2の場合
      # dns = ["8.8.8.7", "8.8.8.8"]  # GoogleのDNS

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Creates a subnet on a specified network.')
      parser.add_argument('--name', required=True, help='The subnet name.')
      parser.add_argument('--network_id', required=True, help='The ID of the attached network.')
      parser.add_argument('--cidr', required=True, help='The CIDR.')
      parser.add_argument('--az', nargs='?', default='jp-east-1a', help='The Availability Zone name. default: jp-east-1a')
      parser.add_argument('--dns', nargs='*', default=[], help='DNS server')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()

      name = args.name
      network_id = args.network_id
      cidr = args.cidr
      az = args.az
      dns = args.dns
      dump = args.dump

    main(name=name, network_id=network_id, cidr=cidr, dns_nameservers=dns, az=az, dump=dump)

  # 実行
  run_main()
