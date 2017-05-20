#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/subnets
List subnets
指定したテナントがアクセス権を持っているサブネットを一覧表示する

NOTE:
　・項目が多いので表示を少なくしている（名前でなんとなく類推できるはず）
"""

"""
実行例

GET /v2.0/subnets
====================  ====================================  ====================================  ================
name                  id                                    network_id                            cidr
====================  ====================================  ====================================  ================
inf_az2_fip-pool03-2  06ce74b3-b0e3-44b9-9131-d1b7c93dceb2  abe76a93-87c3-4635-b0f3-40f794165c26  133.162.220.0/24
inf_az2_fip-pool01-4  5079f324-5db0-44ee-92ac-3a6b7977b23f  375c49fa-a706-4676-b55b-2d3554e5db6a  133.162.204.0/24
inf_az2_fip-pool02-1  6241fdc0-fa98-44fb-9749-46b3252d7cde  852e40a7-82a3-4196-8b84-46f55d01ccba  133.162.206.0/24
inf_az2_ext-subnet03  672fa26a-b2c6-407f-aa10-f60309fc0a68  abe76a93-87c3-4635-b0f3-40f794165c26  133.162.216.0/24
inf_az2_fip-pool04-1  7d515a27-e048-44f0-b359-557a8a53b9d5  bfca06b3-0b23-433f-96af-4f54bf963e5f  133.162.219.0/24
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
  url = k5c.EP_NETWORK + "/v2.0/subnets"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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

  # ネットワーク一覧はデータオブジェクトの中の'subnets'キーに配列として入っている
  # "data": {
  #   "subnets": [
  #     {
  #       "gateway_ip": null,
  #       "id": "06ce74b3-b0e3-44b9-9131-d1b7c93dceb2",
  #       "availability_zone": "jp-east-1b",
  #       "dns_nameservers": [],
  #       "tenant_id": "31ceb599e8ff48aeb66f2fd748988960",
  #       "ip_version": 4,
  #       "host_routes": [],
  #       "enable_dhcp": false,
  #       "network_id": "abe76a93-87c3-4635-b0f3-40f794165c26",
  #       "cidr": "133.162.220.0/24",
  #       "allocation_pools": [
  #         {
  #           "end": "133.162.220.254",
  #           "start": "133.162.220.1"
  #         }
  #       ],
  #       "name": "inf_az2_fip-pool03-2"
  #     },

  subnets_list = []
  for item in data.get('subnets', []):
    subnets_list.append([item.get('id', ''), item.get('name', ''), item.get('network_id', ''), item.get('cidr', '')])

  # 一覧を表示
  print("GET /v2.0/subnets")
  print(tabulate(subnets_list, headers=['id', 'name', 'network_id', 'cidr'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List subnets')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
