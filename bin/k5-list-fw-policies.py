#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/fw/firewall_policies
List firewall policies
ファイアーウォールポリシーの一覧を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-fw-policies.py
GET /v2.0/fw/firewall_policies
====================================  ======  ==============  ================================  ==========
id                                    name      num of rules  tenant_id                         az
====================================  ======  ==============  ================================  ==========
48b2d571-a26d-42b3-934b-5c21cc2ee133  test                12  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
84417ab6-53ea-4595-9d92-7a9d9a552e12  iida                 0  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
b3fbca64-6a97-458f-a92f-36ad899bf87f  test                 0  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
c6f4f5f6-734c-4198-b3fe-40a7a5712109  test                 0  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ======  ==============  ================================  ==========
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
def print_result(result, unused=False):
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

  # ポリシーの一覧はデータオブジェクトの中の'firewall_policies'キーに配列として入っている
  #"data": {
  #  "firewall_policies": [
  #    {
  #      "name": "test",
  #      "firewall_rules": [
  #        "867e35c5-2875-4c51-af31-4cf7932f17f6",
  #        "9597ea56-e39d-4160-bdca-ebf2aca23aab",
  #        "589d96ad-79e9-4a84-b923-10145469643c",
  #        "c44321b7-6b04-4ec4-8e62-dc080794f59b",
  #        "57fbe4aa-6edf-4123-8b6c-c8233cfb3c70",
  #        "6eb8b10f-0756-460a-8b6a-8dd3db77173d",
  #        "58dfdc2f-bf23-481b-9f3a-4b96df6232a2",
  #        "75877f59-7a26-4a59-a343-9e2955dfb49e",
  #        "8cf91195-d611-489d-b322-e28cab2ba705",
  #        "acfada3d-0527-43e7-ba4d-6403ca8654fe",
  #        "3750f08f-5567-4ad7-870f-dd830cc898b0",
  #        "bc8f66e6-c09c-448f-869c-96f2c0843e81"
  #      ],
  #      "audited": false,
  #      "description": "",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "shared": false,
  #      "availability_zone": "jp-east-1a",
  #      "id": "48b2d571-a26d-42b3-934b-5c21cc2ee133"
  #    },

  disp_keys = ['id', 'name', 'firewall_rules', 'tenant_id', 'availability_zone']

  disp_list = []

  for item in data.get('firewall_policies', []):
    # unusedフラグが立っていたら割り当てルールがゼロのポリシーだけを処理する
    if unused:
      if len(item.get('firewall_rules', [])) > 0:
        continue

    row = []
    for key in disp_keys:
      if key == 'firewall_rules':
        row.append(len(item.get('firewall_rules', [])))
      else:
        row.append(item.get(key, ''))
    disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の2番めの要素なのでインデックスは1
  disp_list = sorted(disp_list, key=lambda x: x[1])

  # 一覧を表示
  print("GET /v2.0/fw/firewall_policies")
  print(tabulate(disp_list, headers=['id', 'name', 'num of rules', 'tenant_id', 'az'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists firewall policies.')
    parser.add_argument('--unused', action='store_true', default=False, help='List unused firewall policies.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    unused = args.unused
    dump = args.dump

    # 実行
    result = access_api()

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result, unused=unused)

    return 0


  # 実行
  sys.exit(main())
