#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/fw/firewall_rules
List firewall rules
ファイアーウォールのルールの一覧表示をする

NOTE:
　・表示が横長になるので、情報を減らしてます
"""

"""
実行例

bash-4.4$ ./bin/k5-list-fw-rules.py
/v2.0/fw/firewall_rules
====================================  =============================  ==========  ========  ==========  ===================
id                                    name                             position  action    protocol    availability_zone
====================================  =============================  ==========  ========  ==========  ===================
618c64c3-f28b-404a-ad62-7bec33d7f48b  iida-az1-p01-net02-any-tcp              1  allow     tcp         jp-east-1a
b7077240-adb1-4216-8983-6aa3f1e48d01  iida-az1-p01-net02-any-udp              2  allow     udp         jp-east-1a
9d4138ed-3236-4d50-a637-762b22ffc716  iida-az1-p01-net02-any-icmp             3  allow     icmp        jp-east-1a
0c48089e-f8f2-4eb5-ab4e-f40bf11b91aa  iida-az1-p01-net01-net02-tcp            4  deny      tcp         jp-east-1a
76dcbfc1-6593-4c9a-91b9-ff7223f4d358  iida-az1-p01-net01-net02-udp            5  deny      udp         jp-east-1a
d621e8bf-c9c6-485c-b96c-7a09887935fe  iida-az1-p01-net01-net02-icmp           6  deny      icmp        jp-east-1a
abded572-ed04-4527-a6b2-1f728a926a81  iida-az1-p01-net01-any-tcp              7  allow     tcp         jp-east-1a
5ef0625e-3f85-435e-a5e7-e1812ffbc173  iida-az1-p01-net01-any-udp              8  allow     udp         jp-east-1a
af357dcf-2d4e-4c02-8ec5-3db261665daf  iida-az1-p01-net01-any-icmp             9  allow     icmp        jp-east-1a
cd2249f9-9f7a-42e5-94cb-8a528abeae04  deny-all-tcp                           10  deny      tcp         jp-east-1a
5925fef4-392b-4ff6-9962-94a79e8a9973  deny-all-udp                           11  deny      udp         jp-east-1a
0b429ceb-e665-48f9-b695-2c0ca9357bea  deny-all-icmp                          12  deny      icmp        jp-east-1a
====================================  =============================  ==========  ========  ==========  ===================
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
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_rules"

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

  # ルール一覧はデータオブジェクトの中の'firewall_rules'キーに配列として入っている
  #"data": {
  #  "firewall_rules": [
  #    {
  #      "action": "allow",
  #      "ip_version": 4,
  #      "shared": false,
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "firewall_policy_id": null,
  #      "availability_zone": "jp-east-1a",
  #      "source_port": null,
  #      "source_ip_address": "133.162.192.0/24",
  #      "id": "856e5fa9-f114-403f-aae0-f9ef3ffd3f0c",
  #      "description": "test",
  #      "name": "iida-az1-p01-mgmt01-any-udp",
  #      "destination_port": null,
  #      "destination_ip_address": null,
  #      "protocol": "udp",
  #      "position": null,
  #      "enabled": true
  #    }
  #  ]
  #}

  # firewall_rulesキーの値を取り出す
  firewall_rules = data.get('firewall_rules', [])

  # positionキーの値でソートする
  if firewall_rules:
    # positionキーの値がNoneだとソートできないので""に置き換える
    for rule in firewall_rules:
      if rule.get('position', None) is None:
        rule['position'] = ""
    # sorted()を使ってソートする
    firewall_rules = sorted(firewall_rules, key=lambda x: x.get('position', 0))

  # 表示項目
  keys = ['id', 'name', 'position', 'action', 'protocol', 'availability_zone']

  # tabulateで表示するための配列
  rules_list = []
  for rule in firewall_rules:
    items = []
    for key in keys:
      items.append(rule.get(key, ''))
    rules_list.append(items)

  # 一覧を表示
  print("/v2.0/fw/firewall_rules")
  print(tabulate(rules_list, headers=keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Lists firewall rules.')
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
