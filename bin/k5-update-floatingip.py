#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}
Update router
指定したルータの情報を更新する

NOTE:
　・用意しておいた別のポートにフローティングIPを差し替えます
"""

"""
実行例

bash-4.4$ ./bin/k5-update-floatingip.py \
--floatingip-id 5654254d-0f36-425d-ae89-6e827fc99e54 \
--port-id 6ec9de23-9e3c-4cf1-99be-f3b84b915b24

/v2.0/floatingips
===================  ====================================
id                   5654254d-0f36-425d-ae89-6e827fc99e54
floating_ip_address  133.162.215.230
fixed_ip_address     10.1.1.200
status               DOWN
port_id              6ec9de23-9e3c-4cf1-99be-f3b84b915b24
router_id            ffbd70be-24cf-4dff-a4f6-661bf892e313
availability_zone    jp-east-1a
tenant_id            a5001a8b9c4a4712985c11377bd6d4fe
===================  ====================================
bash-4.4$
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
def make_request_data(port_id=""):
  """リクエストデータを作成して返却します"""

  floatingip_object = {
    'port_id': port_id
  }

  return {'floatingip': floatingip_object}


#
# APIにアクセスする
#
def access_api(floatingip_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK +  "/v2.0/floatingips/" + floatingip_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッド
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
    # ステータスコードが503の場合は2分後に実行を促す
    if status_code == 503:
      print("\nNOTE:")
      print("External gateway is being configured. Please try it again about 2 minutes later.")
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # フローティングIPの情報はデータオブジェクトの中の'floatingip'キーにオブジェクトとして入っている
  #{
  #  "data": {
  #    "floatingip": {
  #      "floating_ip_address": "133.162.215.224",
  #      "status": "DOWN",
  #      "id": "6254e6f4-e3bb-4824-a390-110a883d4281",
  #      "fixed_ip_address": "10.1.1.100",
  #      "port_id": "77297e3a-7135-4fb4-8024-e677d9df66d4",
  #      "availability_zone": "jp-east-1a",
  #      "floating_network_id": "cd4057bd-f72e-4244-a7dd-1bcb2775dd67",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 201
  #}
  fip = data.get('floatingip', {})

  disp_keys = ['id', 'floating_ip_address', 'fixed_ip_address', 'status', 'port_id', 'router_id', 'availability_zone', 'tenant_id']

  # 表示用に配列にする
  fip_list = []
  for key in disp_keys:
    fip_list.append([key, fip.get(key, '')])

  # 表示
  print("/v2.0/floatingips")
  print(tabulate(fip_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Updates a floating IP and its association with an internal port.')
    parser.add_argument('--floatingip-id', dest='floatingip_id', metavar='id', required=True, help='The UUID of the floating IP.')
    parser.add_argument('--port-id', dest='port_id', metavar='id', required=True, help='The port id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    floatingip_id = args.floatingip_id
    port_id = args.port_id
    dump = args.dump

    # リクエストデータを作成
    data = make_request_data(port_id=port_id)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(floatingip_id=floatingip_id, data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
