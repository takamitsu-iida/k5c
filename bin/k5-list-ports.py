#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/ports
List ports
テナントがアクセスするポートの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-ports.py
GET /v2.0/ports
====================================  =====================  ====================================  ==============  =================
id                                    name                   network_id                            device_owner    mac_address
====================================  =====================  ====================================  ==============  =================
53bcf745-45b0-4b06-bb21-445ff85060cc                         ce5ae176-3478-45c0-9a8f-59975e4ba28d  network:dhcp    fa:16:3e:cb:18:ed
869ee3b5-9371-41ea-aff5-64dbd214d3b7  iida-network-1-port-1  ce5ae176-3478-45c0-9a8f-59975e4ba28d                  fa:16:3e:5e:5d:95
====================================  =====================  ====================================  ==============  =================
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
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/ports"

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

  # ポート一覧はデータオブジェクトの中の'ports'キーに配列として入っている
  #"data": {
  #  "ports": [
  #    {
  #      "binding:vnic_type": "normal",
  #      "security_groups": [],
  #      "extra_dhcp_opts": [],
  #      "id": "53bcf745-45b0-4b06-bb21-445ff85060cc",
  #      "mac_address": "fa:16:3e:cb:18:ed",
  #      "availability_zone": "jp-east-1a",
  #      "name": "",
  #      "admin_state_up": true,
  #      "status": "ACTIVE",
  #      "fixed_ips": [
  #        {
  #          "subnet_id": "8ed6dd7b-2ae3-4f68-81c9-e5d9e074b67a",
  #          "ip_address": "192.168.0.3"
  #        }
  #      ],
  #      "device_owner": "network:dhcp",
  #      "network_id": "ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #      "device_id": "dhcp097c8e8d-5a8a-5917-8ded-3b559df68635-ce5ae176-3478-45c0-9a8f-59975e4ba28d",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "allowed_address_pairs": []
  #    },
  ports_list = []
  for item in data.get('ports', []):
    ports_list.append([item.get('id', ''), item.get('name', ''), item.get('network_id', ''), item.get('device_owner', ''), item.get('mac_address', '')])

  # 一覧を表示
  print("GET /v2.0/ports")
  print(tabulate(ports_list, headers=['id', 'name', 'network_id', 'device_owner', 'mac_address'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List ports')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
