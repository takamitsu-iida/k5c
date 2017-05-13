#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}
Update extra route
ルーティング情報をアップデートする

NOTE:
　・設定ファイルが必要です k5-update-extra-routes.yaml
"""

"""
実行例

bash-4.4$ ./k5-update-extra-routes.py --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================

external_gateway_info
===========  ====================================
enable_snat  True
network_id   cd4057bd-f72e-4244-a7dd-1bcb2775dd67
===========  ====================================

routes
==============  =========
destination     nexthop
==============  =========
10.0.0.0/8      10.1.2.9
172.16.0.0/12   10.1.2.9
192.168.0.0/16  10.1.2.9
==============  =========
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
def main(router_id="", routes=None, dump=False):
  """メイン関数"""
  # pylint: disable=too-many-arguments

  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/routers/" + router_id

  # 変更するルータのオブジェクト
  router_object = {
    'router': {
      'routes': routes
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
  r = c.put(url=url, data=router_object)

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

  # 変更したサブネットの情報はデータオブジェクトの中の'subnet'キーにオブジェクトとして入っている
  # "data": {
  #   "router": {
  #     "routes": [
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "10.0.0.0/8"
  #       },
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "172.16.0.0/12"
  #       },
  #       {
  #         "nexthop": "10.1.2.9",
  #         "destination": "192.168.0.0/16"
  #       }
  #     ],
  #     "availability_zone": "jp-east-1a",
  #     "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #     "name": "iida-az1-router01",
  #     "status": "ACTIVE",
  #     "admin_state_up": true,
  #     "id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #     "external_gateway_info": {
  #       "network_id": "cd4057bd-f72e-4244-a7dd-1bcb2775dd67",
  #       "enable_snat": true
  #     }
  #   }
  # },

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
  print("PUT /v2.0/routers/{router_id}")
  print(tabulate(rtrs, tablefmt='rst'))

  eginfo = rtr.get('external_gateway_info', None)
  if eginfo:
    eginfo_list = []
    eginfo_list.append(['enable_snat', eginfo.get('enable_snat', '')])
    eginfo_list.append(['network_id', eginfo.get('network_id', '')])
    print("")
    print("external_gateway_info")
    print(tabulate(eginfo_list, tablefmt='rst'))
  else:
    print("")
    print("'external_gateway_info' is not set.")

  # 経路情報一覧を表示
  routes = rtr.get('routes', [])
  if routes:
    routes_list = []
    for item in routes:
      routes_list.append([item.get('destination', ''), item.get('nexthop', '')])
    print("")
    print("routes")
    print(tabulate(routes_list, headers=['destination', 'nexthop'], tablefmt='rst'))
  else:
    print("")
    print("'routes' is not set.")

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:

      # 変更対象のrouter_id
      router_id = "ffbd70be-24cf-4dff-a4f6-661bf892e313"

      routes = [
        {
          'destination': "10.0.0.0/8",
          'nexthop': "10.1.2.9"
        },
        {
          'destination': "172.16.0.0/12",
          'nexthop': "10.1.2.9"
        },
        {
          'destination': "192.168.0.0/16",
          'nexthop': "10.1.2.9"
        }
      ]

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Updates logical router with routes attribute.')
      parser.add_argument('--router_id', required=True, help='The ID of the router.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      router_id = args.router_id
      dump = args.dump

      # 自身の名前から拡張子を除いてプログラム名を得る
      app_name = os.path.splitext(os.path.basename(__file__))[0]

      # コンフィグファイルの名前
      config_file = app_name + ".yaml"

      if not os.path.exists(config_file):
        logging.error("Config file not found. %s", config_file)
        sys.exit(1)

      # コンフィグファイルを読み込む
      import codecs
      import yaml
      with codecs.open(config_file, 'r', 'utf-8') as f:
        try:
          data = yaml.load(f)
        except yaml.YAMLError as e:
          logging.exception(e)
          sys.exit(1)

      config = data.get(router_id, {})
      if not config:
        logging.error("router_id not found in the yaml file.")
        sys.exit(1)

      routes = config.get('routes', [])

    main(router_id=router_id, routes=routes, dump=dump)

  # 実行
  run_main()
