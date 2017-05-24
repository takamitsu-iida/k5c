#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/vpn/vpnservices/{service-id}
Update VPN service

PENDING状態でないVPNサービスを更新する

NOTE:
　・設定ファイルが必要です $app_home/conf/ipsec.yaml
"""

"""
実行例

bash-4.4$ ./bin/k5-list-vpnservices.py
GET /v2.0/vpn/vpnservices
====================================  ===================  ===================
id                                    name                 availability_zone
====================================  ===================  ===================
75f35f53-ecbd-4748-a070-3316435e35cc  iida-az1-vpnservice  jp-east-1a
====================================  ===================  ===================

bash-4.4$ ./bin/k5-update-vpnservice.py \
--service-id 75f35f53-ecbd-4748-a070-3316435e35cc \
--name  iida-az1-vpnservice

POST /v2.0/vpn/vpnservices
=================  ====================================
id                 75f35f53-ecbd-4748-a070-3316435e35cc
name               iida-az1-vpnservice
availability_zone  jp-east-1a
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

  data = config.get('vpnservice', {})

  vpnservice_object = {}

  allowed_keys = ['name', 'admin_state_up', 'description']
  for key in allowed_keys:
    item = data.get(key, None)
    if item:
      vpnservice_object[key] = data.get(key)

  return {'vpnservice': vpnservice_object}


#
# APIにアクセスする
#
def access_api(service_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/vpnservices/" + service_id

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

  # データオブジェクトの中の'vpnservice'キーにオブジェクトとして入っている
  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": {
  #    "vpnservice": {
  #      "admin_state_up": true,
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #      "id": "eea9470f-d2b4-4cf3-9e3f-4368aa4f73d4",
  #      "subnet_id": "abbbbcf4-ea8f-4218-bbe7-669231eeba30",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "availability_zone": "jp-east-1a",
  #      "status": "PENDING_CREATE",
  #      "description": "",
  #      "name": "iida-az1-vpnservice"
  #    }
  #  },
  #  "status_code": 201
  #}
  vpnservice = data.get('vpnservice', {})

  disp_key = ['id', 'name', 'availability_zone']

  # 表示用に配列にする
  vpnservice_list = []
  for key in disp_key:
    row = []
    row.append(key)
    row.append(vpnservice.get(key, ''))
    vpnservice_list.append(row)

  # 表示
  print("POST /v2.0/vpn/vpnservices")
  print(tabulate(vpnservice_list, tablefmt='rst'))


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

    parser = argparse.ArgumentParser(description='Updates a VPN service, provided status is not indicating a PENDING_* state.')
    parser.add_argument('--service-id', dest='service_id', metavar='id', required=True, help="The vpn service id.")
    parser.add_argument('--name', metavar='name', required=True, help='The name of the vpn service.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The configuration file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    service_id = args.service_id
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
    result = access_api(service_id=service_id, data=request_data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
