#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}/add_router_interface
Add interface to router
論理ルータへ内部インターフェースを追加する
"""

"""
実行例(成功)

bash-4.4$ ./k5-connect-router.py  --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --port_id  0001dda0-872e-4f13-9bcd-0eadd27e6b37
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
sys.path.append(here("../lib"))
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
# メイン
#
def main(router_id="", port_id="", dump=False):
  """メイン関数"""
  # 接続先
  url = k5c.EP_NETWORK +  "/v2.0/routers/" + router_id + "/add_router_interface"

  # 接続対象となるインタフェースのオブジェクト
  interface_object = {
    'port_id' : port_id
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=interface_object)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return r

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    return r

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    return r

  # "data": {
  #   "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #   "port_id": "b9fc91fd-6ae9-4c75-be47-94d818a6296f",
  #   "id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #   "availability_zone": "jp-east-1a",
  #   "subnet_id": "abbbbcf4-ea8f-4218-bbe7-669231eeba30"
  # },

  # 表示用に配列にする
  rtrs = []
  rtrs.append(['id', data.get('id', '')])
  rtrs.append(['port_id', data.get('port_id', '')])
  rtrs.append(['subnet_id', data.get('subnet_id', '')])
  rtrs.append(['az', data.get('availability_zone', '')])
  rtrs.append(['tenant_id', data.get('tenant_id', '')])

  # 結果表示
  print("status_code: {0}".format(r.get('status_code', "")))
  print("PUT /v2.0/routers/{router_id}/add_router_interface")
  print(tabulate(rtrs, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:

      # 対象のルータID
      router_id = ""

      # 接続するポートID
      port_id = ""

      # jsonをダンプ
      dump = False
    else:
      import argparse
      parser = argparse.ArgumentParser(description='Adds an internal interface to a logical router.')
      parser.add_argument('--router_id', required=True, help='The router id.')
      parser.add_argument('--port_id', required=True, help='The port id.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      router_id = args.router_id
      port_id = args.port_id
      dump = args.dump

    main(router_id=router_id, port_id=port_id, dump=dump)

  # 実行
  run_main()
