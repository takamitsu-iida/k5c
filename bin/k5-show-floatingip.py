#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/floatingips/{floatingip_id}
Show floating IP details
指定した Floating IP の詳細を表示する
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
def access_api(floatingip_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/floatingips/" + floatingip_id

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

  # フローティングIPの情報はデータオブジェクトの中の'floatingip'キーにオブジェクトとして入っている
  #{
  #  "status_code": 200,
  #  "data": {
  #    "floatingip": {
  #      "floating_network_id": "cd4057bd-f72e-4244-a7dd-1bcb2775dd67",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "availability_zone": "jp-east-1a",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #      "fixed_ip_address": "10.1.1.100",
  #      "floating_ip_address": "133.162.215.230",
  #      "port_id": "77297e3a-7135-4fb4-8024-e677d9df66d4",
  #      "status": "DOWN",
  #      "id": "5654254d-0f36-425d-ae89-6e827fc99e54"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8"
  #}
  fip = data.get('floatingip', {})

  disp_keys = ['id', 'floating_ip_address', 'fixed_ip_address', 'status', 'port_id', 'router_id', 'availability_zone', 'tenant_id']

  # 表示用に配列にする
  fip_list = []
  for key in disp_keys:
    fip_list.append([key, fip.get(key, '')])

  # ネットワーク情報を表示
  print("GET /v2.0/floatingips/{floatingip_id}")
  print(tabulate(fip_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows details for a specified floating IP.')
    parser.add_argument('floatingip_id', metavar='id', help='The UUID of the floating IP.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    floatingip_id = args.floatingip_id
    dump = args.dump

    if floatingip_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          # 実行
          result = access_api(floatingip_id=uuid)
          # 表示
          print(uuid)
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(floatingip_id=floatingip_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
