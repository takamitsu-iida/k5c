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

bash-4.4$ ./bin/k5-list-subnets.py | grep -v inf_
GET /v2.0/subnets
====================================  ====================  ====================================  ================  ===================
id                                    name                  network_id                            cidr              availability_zone
====================================  ====================  ====================================  ================  ===================
abbbbcf4-ea8f-4218-bbe7-669231eeba30  iida-az1-subnet01     8f15da62-c7e5-47ec-8668-ee502f6d00d2  10.1.1.0/24       jp-east-1a
2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6  iida-az1-subnet02     e3c166c0-7e90-4c6e-857e-87fd985f98ac  10.1.2.0/24       jp-east-1a
07041634-9f01-4518-a2c8-1e6ea8d956ee  iida-az2-subnet01     0cbf1e4d-479b-4336-8ba9-eb530fe55adb  10.2.1.0/24       jp-east-1b
50bf50fa-816b-4e7e-98da-8379d9675101  iida-az2-subnet02     8b004a16-c5a2-4e1d-ab9e-a417fef45ec7  10.2.2.0/24       jp-east-1b
====================================  ====================  ====================================  ================  ===================
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

  # disp_keys = ['id', 'name', 'network_id', 'cidr']
  disp_keys = ['id', 'name', 'network_id', 'cidr', 'availability_zone']

  # 表示用の配列
  disp_list = []
  for item in data.get('subnets', []):
    if az is None or item.get('availability_zone', "") == az:
      row = []
      for key in disp_keys:
        row.append(item.get(key, ''))
      disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/subnets")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List subnets')
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
