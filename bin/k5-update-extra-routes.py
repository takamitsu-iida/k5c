#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}
Update extra route
ルーティング情報をアップデートする

NOTE:
　・設定ファイルが必要です conf/extra-routes.yaml
"""

"""
実行例

bash-4.4$ ./bin/k5-update-extra-routes.py ffbd70be-24cf-4dff-a4f6-661bf892e313 --filename conf/extra-routes.yaml
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
network_id   92f386c1-59fe-48ca-8cf9-b95f81920466
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
def make_request_data(routes=None):
  """リクエストデータを作成して返却します"""

  routes_object = {
    'routes': routes
  }

  return {'router': routes_object}


#
# APIにアクセスする
#
def access_api(router_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/routers/" + router_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
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
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

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


if __name__ == '__main__':

  import argparse
  import codecs
  import yaml

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # デフォルトのコンフィグファイルの名前
    # $app_home/conf/extra-routes.yaml
    config_file = os.path.join(app_home, "conf", "extra-routes.yaml")

    parser = argparse.ArgumentParser(description='Updates logical router with routes attribute.')
    parser.add_argument('router_id', help='The ID of the router.')
    parser.add_argument('--filename', dest='filename', metavar='file', default=config_file, help='The rule file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    router_id = args.router_id
    filename = args.filename
    dump = args.dump

    if not os.path.exists(filename):
      logging.error("Config file not found. %s", filename)
      return 1

    # コンフィグファイルを読み込む
    with codecs.open(filename, 'r', 'utf-8') as f:
      try:
        yaml_data = yaml.load(f)
      except yaml.YAMLError as e:
        logging.exception("YAMLファイルにエラーがあります %s", e)
        return 1

    router_data = yaml_data.get(router_id, {})
    if not router_data:
      logging.error("router_id not found in the yaml file.")
      return 1

    routes = router_data.get('routes', [])

    # リクエストデータを作成
    data = make_request_data(routes=routes)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(router_id=router_id, data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
