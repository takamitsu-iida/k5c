#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/routers
Create router
論理ルータを作成する

NOTE:
"""

"""
実行例

bash-4.4$ ./bin/k5-create-router.py --name iida-az1-router02
POST /v2.0/routers
==============  ====================================
name            iida-az1-router02
id              c78bcffe-10ca-4cb6-a67e-0712249fcc0e
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
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
# リクエストデータを作成する
#
def make_request_data(name="", az=""):
  """リクエストデータを作成して返却します"""

  # 作成するルータの情報
  router_object = {
    'router': {
      'name': name,
      'admin_state_up': True,  # 常時True
      'availability_zone': az
    }
  }

  return router_object


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK +  "/v2.0/routers"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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

  # 作成したルータの情報はデータオブジェクトの中の'router'キーにオブジェクトとして入っている
  #"data": {
  #  "router": {
  #    "admin_state_up": true,
  #    "id": "ad3ddc47-6303-48e8-87ad-cb0333c93112",
  #    "name": "iida-test-router-1",
  #    "external_gateway_info": null,
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "status": "ACTIVE",
  #    "availability_zone": "jp-east-1a"
  #  }
  #}
  rtr = data.get('router', {})

  # 表示用に配列にする
  rtrs = []
  rtrs.append(['name', rtr.get('name', '')])
  rtrs.append(['id', rtr.get('id', '')])
  rtrs.append(['az', rtr.get('availability_zone', '')])
  rtrs.append(['tenant_id', rtr.get('tenant_id', '')])
  rtrs.append(['status', rtr.get('status', '')])
  rtrs.append(['admin_state_up', rtr.get('admin_state_up', '')])

  # 表示
  print("POST /v2.0/routers")
  print(tabulate(rtrs, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Creates a logical router.')
    parser.add_argument('--name', metavar='name', required=True, help='The router name.')
    parser.add_argument('--az', nargs='?', default='jp-east-1a', help='The Availability Zone name. default: jp-east-1a')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    az = args.az
    dump = args.dump

    # 作成するルータの名前
    # name = "iida-ext-router-1"
    #
    # 作成する場所
    # az = "jp-east-1a"
    # az = "jp-east-1b"
    #
    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(name=name, az=az)

    # 実行
    result = access_api(data=data)

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
