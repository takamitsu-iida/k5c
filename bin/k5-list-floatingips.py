#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/floatingips
List floating IPs
Floating IPの一覧を表示する
"""

"""
実行例

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
  url = k5c.EP_NETWORK + "/v2.0/floatingips"

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

  # フローティングIP一覧はデータオブジェクトの中の'floatingips'キーに配列として入っている
  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": {
  #    "floatingips": [
  #      {
  #        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #        "floating_ip_address": "133.162.215.220",
  #        "status": "DOWN",
  #        "floating_network_id": "cd4057bd-f72e-4244-a7dd-1bcb2775dd67",
  #        "availability_zone": "jp-east-1a",
  #        "fixed_ip_address": "10.1.1.100",
  #        "port_id": "77297e3a-7135-4fb4-8024-e677d9df66d4",
  #        "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #        "id": "2b9f1017-393e-4d8e-9807-e5ac309f56a7"
  #      }
  #    ]
  #  },
  #  "status_code": 200
  #}

  # disp_keys = ['id', 'floating_ip_address', 'fixed_ip_address', 'port_id', 'router_id', 'status']
  disp_keys = ['id', 'floating_ip_address', 'fixed_ip_address', 'status']

  floatingips_list = []
  for item in data.get('floatingips', []):
    row = []
    for key in disp_keys:
      row.append(item.get(key, ''))
    floatingips_list.append(row)

  # 一覧を表示
  print("/v2.0/floatingips")
  print(tabulate(floatingips_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists floating IPs that are accessible to the tenant who submits the request.')
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
