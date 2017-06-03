#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/vpn/ipsec-site-connections/{connection-id}
Update IPSec site connection
PENDING状態でないIPsecサイト間接続を更新する

NOTE:
　・設定ファイルが必要です $app_home/conf/ipsec.yaml
"""

"""
実行例

bash-4.4$ ./bin/k5-list-site-connections.py
GET /v2.0/vpn/ipsec-site-connections
====================================  ======================  ==============  ========  ===================
id                                    name                    peer_address    status    availability_zone
====================================  ======================  ==============  ========  ===================
ffe2f03d-be54-4b4f-8624-cc7e6b020fb9  iida-az1-connection-01  2.2.2.2         DOWN      jp-east-1a
====================================  ======================  ==============  ========  ===================

bash-4.4$ ./bin/k5-update-site-connection.py \
--connection-id ffe2f03d-be54-4b4f-8624-cc7e6b020fb9 \
--name iida-az1-connection-01

PUT /v2.0/vpn/ipsec-site-connections
=================  ====================================
name               iida-az1-connection-01
id                 ffe2f03d-be54-4b4f-8624-cc7e6b020fb9
peer_address       2.2.2.2
peer_id            2.2.2.2
psk                passpass
vpnservice_id      37ab0e56-1ff1-4dbe-acce-fd7ed1a3773a
ikepolicy_id       4334b806-824c-4419-b0cb-b79fa8be9c72
ipsecpolicy_id     ab659e26-327b-4aff-b727-b039da09f22e
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
def make_request_data(config=None):
  """リクエストデータを作成して返却します"""

  d = config.get('vpnservice', {})

  # YAMLファイルから読んだデータをまるごと信用すると危ないので作り変える
  connection_object = {}

  allowed_keys = [
    'psk', 'initiator', 'admin_state_up', 'peer_cidrs',
    'dpd', 'peer_address', 'peer_id', 'name', 'description'
  ]

  for key in allowed_keys:
    item = d.get(key, None)
    if item:
      connection_object[key] = d.get(key)

  return {'ipsec_site_connection': connection_object}


#
# APIにアクセスする
#
def access_api(connection_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsec-site-connections/" + connection_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

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

  print("PUT /v2.0/vpn/ipsec-site-connections")
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

    parser = argparse.ArgumentParser(description='Updates an IPSec site-to-site connection, provided status is not indicating a PENDING_* state.')
    parser.add_argument('--connection-id', dest='connection_id', metavar='id', required=True, help="The ipsec site connection id.")
    parser.add_argument('--name', metavar='name', required=True, help='The name of the vpn service.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The configuration file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    connection_id = args.connection_id
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
    result = access_api(connection_id=connection_id, data=request_data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
