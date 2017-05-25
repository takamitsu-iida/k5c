#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/vpn/ipsec-site-connections
Create IPSec site connection
IPsecのサイト接続を作成する

NOTE:
　・設定ファイルが必要です $app_home/conf/ipsec.yaml
"""

"""
実行例

bash-4.4$ ./bin/k5-create-site-connection.py --name iida-az1-connection-01
POST /v2.0/vpn/ipsec-site-connections
=================  ====================================
name               iida-az1-connection-01
id                 4273f817-da1c-4aa5-9445-6501d5bed29d
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
status             PENDING_CREATE
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
availability_zone  jp-east-1a
description
=================  ====================================
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
  sys.exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# リクエストデータを作成する
#
def make_request_data(config=None):
  """リクエストデータを作成して返却します"""

  d = config.get('vpnservice', {})

  # YAMLファイルから読んだデータをまるごと信用すると危ないので作り変える
  connection_object = {}

  allowed_keys = [
    'psk', 'initiator', 'ipsecpolicy_id', 'admin_state_up', 'peer_cidrs', 'ikepolicy_id',
    'dpd', 'vpnservice_id', 'peer_address', 'peer_id', 'name', 'description', 'availability_zone'
  ]

  for key in allowed_keys:
    item = d.get(key, None)
    if item:
      connection_object[key] = d.get(key)

  return {'ipsec_site_connection': connection_object}


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsec-site-connections"

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

  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": {
  #    "ipsec_site_connection": {
  #      "dpd": {
  #        "timeout": 30,
  #        "action": "restart",
  #        "interval": 10
  #      },
  #      "vpnservice_id": "75f35f53-ecbd-4748-a070-3316435e35cc",
  #      "description": "",
  #      "peer_address": "1.1.1.1",
  #      "mtu": 1500,
  #      "route_mode": "static",
  #      "status": "PENDING_CREATE",
  #      "initiator": "bi-directional",
  #      "name": "iida-az1-connection-01",
  #      "auth_mode": "psk",
  #      "ipsecpolicy_id": "26525271-0337-4ad2-b0d3-120814fc0794",
  #      "psk": "passpass",
  #      "ikepolicy_id": "9fc16042-95ae-46b9-84bc-4777b3b9f89c",
  #      "peer_id": "x.x.x.x",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "availability_zone": "jp-east-1a",
  #      "id": "deb952b8-1b7b-4cae-924e-396e664dd7b0",
  #      "peer_cidrs": [
  #        "10.1.1.0/24"
  #      ],
  #      "admin_state_up": true
  #    }
  #  },
  #  "status_code": 201
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

  print("POST /v2.0/vpn/ipsec-site-connections")
  print(tabulate(disp_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse
  import codecs
  import yaml

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # デフォルトのコンフィグファイルの名前
    # $app_home/conf/ipsec.yaml
    config_file = os.path.join(app_home, "conf", "ipsec.yaml")

    parser = argparse.ArgumentParser(description='Creates an IPSec site connection.')
    parser.add_argument('--name', metavar='name', required=True, help='The name of the vpn service.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The configuration file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    dump = args.dump

    if not os.path.exists(config_file):
      logging.error("Config file not found. %s", config_file)
      return 1

    with codecs.open(config_file, 'r', 'utf-8') as f:
      try:
        data = yaml.load(f)
      except yaml.YAMLError:
        logging.error("YAML error")
        return 1

    config = data.get(name, {})
    if not config:
      logging.error("name not found in the yaml file.")
      return 1

    request_data = make_request_data(config=config)

    # 実行
    result = access_api(data=request_data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
