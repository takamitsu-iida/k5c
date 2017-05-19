#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/fw/firewall_policies
List firewall policies
ファイアーウォールポリシーの一覧を表示する
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
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_policies"

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

  # ネットワーク一覧はデータオブジェクトの中の'networks'キーに配列として入っている
  #"data": {
  #  "networks": [
  #    {
  #      "availability_zone": "jp-east-1b",
  #      "name": "inf_az2_ext-net01",
  #      "id": "375c49fa-a706-4676-b55b-2d3554e5db6a",
  #      "tenant_id": "31ceb599e8ff48aeb66f2fd748988960",
  #      "admin_state_up": true,
  #      "status": "ACTIVE",
  #      "router:external": true,
  #      "subnets": [
  #        "5079f324-5db0-44ee-92ac-3a6b7977b23f",
  #        "a56b6058-0479-43a1-8b27-01c1c05e96a2",
  #        "c1da3ee7-51c3-4801-bb97-aa03a4383ef0",
  #        "e96e55b8-84bb-4777-a782-a5d6e8340039",
  #        "f5e9ec37-88ec-494b-ac55-dae101a54cc1"
  #      ],
  #      "shared": true
  #    },
  networks_list = []
  for item in data.get('networks', []):
    networks_list.append([item.get('id', ''), item.get('name', ''), item.get('tenant_id', ''), item.get('availability_zone', ''), item.get('status', '')])

  # 一覧を表示
  print("GET /v2.0/fw/firewall_policies")
  print(tabulate(networks_list, headers=['id', 'name', 'tenant_id', 'az', 'status'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists firewall policies.')
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
