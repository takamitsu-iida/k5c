#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/routers
List routers
テナント内でアクセス可能なルータのリストを表示する。
"""

"""
実行例

bash-4.4$ ./bin/k5-list-routers.py
GET /v2.0/routers
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
ffbd70be-24cf-4dff-a4f6-661bf892e313  iida-az1-router01  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========
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
# APIにアクセスする
#
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/routers"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  return r


#
# 結果を表示する
#
def print_result(result, az=None):
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

  # ルータ一覧はデータオブジェクトの中の'routers'キーに配列として入っている
  #"data": {
  #  "routers": [
  #    {
  #      "routes": [],
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "status": "ACTIVE",
  #      "name": "iida-test-router-1",
  #      "id": "5359cce0-cd5c-48e8-891a-659c5ae62f65",
  #      "external_gateway_info": null,
  #      "availability_zone": "jp-east-1a",
  #      "admin_state_up": true
  #    },

  disp_keys = ['id', 'name', 'tenant_id', 'availability_zone', 'status']

  disp_list = []
  for item in data.get('routers', []):
    if az is None or item.get('availability_zone', "") == az:
      row = []
      for key in disp_keys:
        row.append(item.get(key, ''))
      disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/routers")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List routers')
    parser.add_argument('--az', nargs='?', default=None, help='The Availability Zone name to display.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    az = args.az
    dump = args.dump

    # 実行
    result = access_api()

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result, az=az)

    return 0


  # 実行
  sys.exit(main())
