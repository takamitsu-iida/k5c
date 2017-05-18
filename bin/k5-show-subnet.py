#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/subnets/{subnet_id}
Show subnet
指定したサブネットの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-subnet.py 38701f66-4610-493f-9c15-78f81917f362
GET /v2.0/subnets/{subnet_id}
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
# APIにアクセスする
#
def access_api(subnet_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/subnets/" + subnet_id

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

  # サブネット情報はデータオブジェクトの中の'subnet'キーにオブジェクトとして入っている
  #"data": {
  #  "subnet": {
  #    "cidr": "192.168.0.0/24",
  #    "name": "iida-subnet-1",
  #    "availability_zone": "jp-east-1a",
  #    "allocation_pools": [
  #      {
  #        "start": "192.168.0.2",
  #        "end": "192.168.0.254"
  #      }
  #    ],
  #    "ip_version": 4,
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "gateway_ip": "192.168.0.1",
  #    "dns_nameservers": [],
  #    "network_id": "ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #    "enable_dhcp": true,
  #    "host_routes": [],
  #    "id": "8ed6dd7b-2ae3-4f68-81c9-e5d9e074b67a"
  #  }
  #},
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
  print("GET /v2.0/subnets/{subnet_id}")
  print(tabulate(subnets, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows information for a specified subnet.')
    parser.add_argument('subnet_id', help='Subnet id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    subnet_id = args.subnet_id
    dump = args.dump

    # 実行
    result = access_api(subnet_id=subnet_id)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
