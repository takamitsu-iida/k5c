#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/subnets/{subnet_id}
Update subnet
指定されたサブネットを更新する

NOTE:
　・設定ファイルが必要です k5-update-subnet.yaml
"""

"""
実行例

bash-4.4$ ./k5-update-subnet.py --subnet_id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
PUT /v2.0/subnets/{subnet_id}
===========  ====================================
name         iida-az1-subnet02
id           2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
az           jp-east-1a
cidr         10.1.2.0/24
gateway_ip   10.1.2.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   e3c166c0-7e90-4c6e-857e-87fd985f98ac
enable_dhcp  True
===========  ====================================


=================
dns_nameservers
=================
133.162.193.9
133.162.193.10
=================


==============  =========
destination     nexthop
==============  =========
172.16.0.0/12   10.1.2.9
192.168.0.0/16  10.1.2.9
10.0.0.0/8      10.1.2.9
==============  =========
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
# リクエストデータを作成する
#
def make_request_data(name=None, gateway_ip=None, dns_nameservers=None, host_routes=None):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  # 作成するサブネットのオブジェクト
  subnet_object = {}

  # nameが指定されていたら追加
  if name:
    subnet_object['name'] = name

  # gateway_ipが指定されていたら追加
  if gateway_ip:
    subnet_object['gateway_ip'] = gateway_ip

  # dns_serversが指定されていたら追加
  if dns_nameservers and len(dns_nameservers) > 0:
    subnet_object['dns_nameservers'] = dns_nameservers

  # host_routesが指定されていたら追加
  if host_routes and len(host_routes) > 0:
    subnet_object['host_routes'] = host_routes

  return {'subnet': subnet_object}


#
# APIにアクセスする
#
def access_api(subnet_id="", data=None):
  """メイン関数"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/subnets/" + subnet_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

  return r


#
# 結果を表示する
#
def print_result(result=None, dump=False):
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

  # 変更したサブネットの情報はデータオブジェクトの中の'subnet'キーにオブジェクトとして入っている
  # "data": {
  #   "subnet": {
  #     "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #     "dns_nameservers": [
  #       "133.162.193.9",
  #       "133.162.193.10"
  #     ],
  #     "ip_version": 4,
  #     "cidr": "10.1.2.0/24",
  #     "network_id": "e3c166c0-7e90-4c6e-857e-87fd985f98ac",
  #     "gateway_ip": "10.1.2.1",
  #     "host_routes": [
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "172.16.0.0/12"
  #       },
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "192.168.0.0/16"
  #       },
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "10.0.0.0/8"
  #       }
  #     ],
  #     "name": "iida-az1-subnet02",
  #     "enable_dhcp": true,
  #     "allocation_pools": [
  #       {
  #         "start": "10.1.2.2",
  #         "end": "10.1.2.254"
  #       }
  #     ],
  #     "id": "2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6",
  #     "availability_zone": "jp-east-1a"
  #   }
  # }
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
  print("PUT /v2.0/subnets/{subnet_id}")
  print(tabulate(subnets, tablefmt='rst'))

  dns_list = []
  for item in sn.get('dns_nameservers', []):
    dns_list.append([item])
  print("\n")
  print(tabulate(dns_list, headers=['dns_nameservers'], tablefmt='rst'))

  routes_list = []
  for item in sn.get('host_routes', []):
    routes_list.append([item.get('destination', ''), item.get('nexthop', '')])
  print("\n")
  print(tabulate(routes_list, headers=['destination', 'nexthop'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse
  import codecs
  import yaml

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # 自身の名前から拡張子を除いてプログラム名を得る
    app_name = os.path.splitext(os.path.basename(__file__))[0]

    # デフォルトのコンフィグファイルの名前
    # 設定ファイルのパス
    # $app_home/conf/update-subnet.yaml
    config_file = os.path.join(app_home, app_name + ".yaml")

    parser = argparse.ArgumentParser(description='Updates a specified subnet.')
    parser.add_argument('--subnet_id', required=True, help='The ID of the subnet.')
    parser.add_argument('-f', '--filename', default=config_file, help='The configuration file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    subnet_id = args.subnet_id
    dump = args.dump

    if not os.path.exists(config_file):
      logging.error("Config file not found. %s", config_file)
      sys.exit(1)

    with codecs.open(config_file, 'r', 'utf-8') as f:
      try:
        data = yaml.load(f)
      except yaml.YAMLError as e:
        logging.exception(e)
        sys.exit(1)

    config = data.get(subnet_id, {})
    if not config:
      logging.error("subnet_id not found in the yaml file.")
      sys.exit(1)

    name = config.get('name', '')
    gateway_ip = config.get('gateway_ip', '')
    dns_nameservers = config.get('dns_nameservers', [])
    host_routes = config.get('host_routes', [])

    data = make_request_data(name=name, gateway_ip=gateway_ip, dns_nameservers=dns_nameservers, host_routes=host_routes)

    if not data:
      logging.error('no rule found.')
      return

    # 実行
    result = access_api(subnet_id=subnet_id, data=data)

    # 得たデータを処理する
    print_result(result=result, dump=dump)


  # 実行
  main()
