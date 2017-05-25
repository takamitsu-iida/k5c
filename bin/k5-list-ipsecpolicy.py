#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/ipsecpolicies
List IPSec policies
IPsecポリシーを一覧表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-ipsecpolicy.py
GET /v2.0/vpn/ipsecpolicies
====================================  ====================  ================================  ===================
id                                    name                  tenant_id                         availability_zone
====================================  ====================  ================================  ===================
bfe2f9f4-7e30-47d6-abab-4fb26be0d735  iida-az1-ipsecpolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ====================  ================================  ===================
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
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsecpolicies"

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
  #  "data": {
  #    "ipsecpolicies": [
  #      {
  #        "encapsulation_mode": "tunnel",
  #        "description": "",
  #        "name": "iida-az1-ipsecpolicy",
  #        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #        "availability_zone": "jp-east-1a",
  #        "lifetime": {
  #          "units": "seconds",
  #          "value": 28800
  #        },
  #        "auth_algorithm": "sha1",
  #        "id": "bfe2f9f4-7e30-47d6-abab-4fb26be0d735",
  #        "encryption_algorithm": "aes-256",
  #        "pfs": "group14",
  #        "transform_protocol": "esp"
  #      }
  #    ]
  #  },
  #  "Content-Type": "application/json;charset=UTF-8"
  #}

  disp_keys = ['id', 'name', 'tenant_id', 'availability_zone']

  disp_list = []
  for item in data.get('ipsecpolicies', []):
    row = []
    for key in disp_keys:
      row.append(item.get(key, ''))
    disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/vpn/ipsecpolicies")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists IKE policies.')
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