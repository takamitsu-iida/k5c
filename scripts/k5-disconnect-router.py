#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}/remove_router_interface
Remove interface from router
論理ルータから内部インターフェースを削除する
"""

"""
実行例

bash-4.4$ ./k5-disconnect-router.py  --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --port_id  0001dda0-872e-4f13-9bcd-0eadd27e6b37
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
  from k5c import k5config  # need info in k5config.py
except ImportError as e:
  logging.exception("k5configモジュールの読み込みに失敗しました: %s", e)
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
  url = k5config.EP_NETWORK + "/v2.0/routers/" + router_id + "/remove_router_interface"

  # 切断対象となるインタフェースのオブジェクト
  port_object = {
    'port_id' : port_id
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=port_object)

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
      router_id = "05dbac99-4058-4f60-a9cc-a7593a681d7b"

      # 切断するポートID
      port_id = "863f2404-4a92-4991-8fab-e4312682dd86"

      # jsonをダンプ
      dump = False
    else:
      import argparse
      parser = argparse.ArgumentParser(description='Removes an internal interface from a logical router.')
      parser.add_argument('--router_id', dest='router_id', required=True, help='The router id.')
      parser.add_argument('--port_id', dest='port_id', required=True, help='The port id.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      router_id = args.router_id
      port_id = args.port_id
      dump = args.dump

    main(router_id=router_id, port_id=port_id, dump=dump)

  # 実行
  run_main()
