#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/vpnservices/{service-id}
Show VPN service details
指定したVPNサービスの詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-vpnservices.py | ./bin/k5-show-vpnservice.py -
vpnservice_id: 5f87861e-54bc-423e-a918-4c7f552c9fde
GET /v2.0/subnets/{subnet_id}
=================  ====================================
name               iida-az1-vpnservice
id                 5f87861e-54bc-423e-a918-4c7f552c9fde
router_id          ffbd70be-24cf-4dff-a4f6-661bf892e313
subnet_id          abbbbcf4-ea8f-4218-bbe7-669231eeba30
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
admin_state_up     True
status             PENDING_CREATE
availability_zone  jp-east-1a
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
def access_api(vpnservice_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/vpnservices/" + vpnservice_id

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
  #    "vpnservice": {
  #      "description": "",
  #      "id": "5f87861e-54bc-423e-a918-4c7f552c9fde",
  #      "subnet_id": "abbbbcf4-ea8f-4218-bbe7-669231eeba30",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "admin_state_up": true,
  #      "name": "iida-az1-vpnservice",
  #      "status": "PENDING_CREATE",
  #      "availability_zone": "jp-east-1a"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 200
  #}

  item = data.get('vpnservice', {})

  disp_keys = ['name', 'id', 'router_id', 'subnet_id', 'tenant_id', 'admin_state_up', 'status', 'availability_zone']

  disp_list = []

  for key in disp_keys:
    row = []
    row.append(key)
    row.append(item.get(key, ''))
    disp_list.append(row)

  print("GET /v2.0/vpn/vpnservices/{service-id}")
  print(tabulate(disp_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows details about a specified VPN service.')
    parser.add_argument('vpnservice_id', metavar='id', help='The vpnservice id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    vpnservice_id = args.vpnservice_id
    dump = args.dump

    if vpnservice_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(vpnservice_id=uuid)
          print("vpnservice_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(vpnservice_id=vpnservice_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
