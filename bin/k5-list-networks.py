#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/networks
List networks
テナントがアクセスするネットワークの一覧を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-networks.py
GET /v2.0/networks
====================================  =================  ================================  ===================  ========
id                                    name               tenant_id                         availability_zone    status
====================================  =================  ================================  ===================  ========
8f15da62-c7e5-47ec-8668-ee502f6d00d2  iida-az1-net01     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a           ACTIVE
e3c166c0-7e90-4c6e-857e-87fd985f98ac  iida-az1-net02     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a           ACTIVE
0cbf1e4d-479b-4336-8ba9-eb530fe55adb  iida-az2-net01     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b           ACTIVE
8b004a16-c5a2-4e1d-ab9e-a417fef45ec7  iida-az2-net02     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b           ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a           ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a           ACTIVE
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a           ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a           ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a           ACTIVE
375c49fa-a706-4676-b55b-2d3554e5db6a  inf_az2_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b           ACTIVE
852e40a7-82a3-4196-8b84-46f55d01ccba  inf_az2_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b           ACTIVE
abe76a93-87c3-4635-b0f3-40f794165c26  inf_az2_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b           ACTIVE
bfca06b3-0b23-433f-96af-4f54bf963e5f  inf_az2_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b           ACTIVE
4516097a-84dd-476f-824a-6b2fd3cc6499  inf_az2_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b           ACTIVE
====================================  =================  ================================  ===================  ========
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
  url = k5c.EP_NETWORK + "/v2.0/networks"

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

  disp_keys = ['id', 'name', 'tenant_id', 'availability_zone', 'status']

  disp_list = []
  for item in data.get('networks', []):
    if az is None or item.get('availability_zone', "") == az:
      row = []
      for key in disp_keys:
        row.append(item.get(key, ''))
      disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  print("GET /v2.0/networks")
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List networks')
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
