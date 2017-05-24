#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/vpnservices
List VPN services
VPNサービスを一覧表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-vpnservices.py
GET /v2.0/vpn/vpnservices
====================================  ===================  ===================
id                                    name                 availability_zone
====================================  ===================  ===================
5f87861e-54bc-423e-a918-4c7f552c9fde  iida-az1-vpnservice  jp-east-1a
====================================  ===================  ===================
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
# APIにアクセスする
#
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/vpnservices"

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
  #  "status_code": 200,
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": {
  #    "vpnservices": [
  #      {
  #        "id": "5f87861e-54bc-423e-a918-4c7f552c9fde",
  #        "subnet_id": "abbbbcf4-ea8f-4218-bbe7-669231eeba30",
  #        "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #        "name": "iida-az1-vpnservice",
  #        "status": "PENDING_CREATE",
  #        "availability_zone": "jp-east-1a",
  #        "admin_state_up": true,
  #        "description": "",
  #        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe"
  #      }
  #    ]
  #  }
  #}

  disp_keys = ['id', 'name', 'availability_zone']

  disp_list = []
  for item in data.get('vpnservices', []):
    row = []
    for key in disp_keys:
      row.append(item.get(key, ''))
    disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/vpn/vpnservices")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists VPN services.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
