#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}/remove_router_interface
Remove interface from router
論理ルータから内部インターフェースを削除する

NOTE:
　- ルータのポートを切断すると、ポートそのものが削除される
"""

"""
実行例

bash-4.4$ ./k5-disconnect-router.py  --router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 --port-id 0001dda0-872e-4f13-9bcd-0eadd27e6b37
status_code: 200
PUT /v2.0/routers/{router_id}/add_router_interface
=========  ====================================
id         ffbd70be-24cf-4dff-a4f6-661bf892e313
port_id    0001dda0-872e-4f13-9bcd-0eadd27e6b37
subnet_id  abbbbcf4-ea8f-4218-bbe7-669231eeba30
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
=========  ====================================
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
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)


#
# リクエストデータを作成する
#
def make_request_data(port_id=""):
  """リクエストデータを作成して返却します"""
  return {'port_id': port_id}


#
# APIにアクセスする
#
def access_api(router_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/routers/" + router_id + "/remove_router_interface"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

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

  # データオブジェクト直下に入っている
  # "data": {
  #   "port_id": "b9fc91fd-6ae9-4c75-be47-94d818a6296f",
  #   "subnet_id": "abbbbcf4-ea8f-4218-bbe7-669231eeba30",
  #   "availability_zone": "jp-east-1a",
  #   "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #   "id": "ffbd70be-24cf-4dff-a4f6-661bf892e313"
  # }

  # 表示用に配列にする
  rtrs = []
  rtrs.append(['id', data.get('id', '')])
  rtrs.append(['port_id', data.get('port_id', '')])
  rtrs.append(['subnet_id', data.get('subnet_id', '')])
  rtrs.append(['az', data.get('availability_zone', '')])
  rtrs.append(['tenant_id', data.get('tenant_id', '')])

  # 結果表示
  print("status_code: {0}".format(result.get('status_code', "")))
  print("PUT /v2.0/routers/{router_id}/add_router_interface")
  print(tabulate(rtrs, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Removes an internal interface from a logical router.')
    parser.add_argument('--router-id', dest='router_id', metavar='id', required=True, help='The router id.')
    parser.add_argument('--port-id', dest='port_id', metavar='id', required=True, help='The port id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    router_id = args.router_id
    port_id = args.port_id
    dump = args.dump

    # 対象のルータID
    # router_id = "ffbd70be-24cf-4dff-a4f6-661bf892e313"

    # 切断するポートID
    # port_id = "863f2404-4a92-4991-8fab-e4312682dd86"

    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(port_id=port_id)

    # 実行
    result = access_api(router_id=router_id, data=data)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
