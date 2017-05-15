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

/v2.0/fw/firewall_rules
====================================  ================================  ==========  ========  ==========  =============  ===================
id                                    name                              position    action    protocol    description    availability_zone
====================================  ================================  ==========  ========  ==========  =============  ===================
00641438-57e2-444c-8f75-227ea11b4598  iida-az1-p01-mgmt01-any-icmp                  allow     icmp        test           jp-east-1a
04f9bbc2-34f3-4b88-8313-def1f6984a9a  iida-az1-p01-mgmt01-any-tcp                   allow     tcp         test           jp-east-1a
12a99347-fcd1-4673-8cbb-bf5ae0b41708  iida-az1-p01-private192-any-icmp              allow     icmp        test           jp-east-1a
15ba5f0e-ee12-4473-9c80-29eb550a644b  iida-az1-p01-any-net01-http                   allow     tcp         test           jp-east-1a
279cfc37-1312-43c7-8a91-0fe2b11a3417  iida-az1-p01-private172-any-icmp              allow     icmp        test           jp-east-1a
550a1bed-0eb7-4088-b135-e00a4fd21047  iida-az1-p01-private10-any-icmp               allow     icmp        test           jp-east-1a
571b7735-8227-4f69-ab64-94e3d3020ae6  iida-az1-p01-net02-any-tcp                    allow     tcp         test           jp-east-1a
7a0c3d0a-294f-4947-a0f2-2891c1a870b2  iida-az1-p01-net02-any-icmp                   allow     icmp        test           jp-east-1a
85fa92d0-97a1-4907-9321-80958cca7b89  iida-az1-p01-any-net01-https                  allow     tcp         test           jp-east-1a
898d75ac-89bc-4cae-bec8-bbf67364e159  iida-az1-p01-net01-any-udp                    allow     udp         test           jp-east-1a
93aa698a-6ccc-4d78-9407-cce67589ffc0  iida-az1-p01-net02-any-udp                    allow     udp         test           jp-east-1a
ae35a22e-71f3-4411-b6c1-eebc6e8c8267  iida-az1-p01-deny-all                         deny                  test           jp-east-1a
dc9f79c7-7793-47f4-95e1-149e54e1b93f  iida-az1-p01-mgmt01-any-udp                   allow     udp         test           jp-east-1a
f693744d-fd92-4f40-83e4-7e33aa55d87c  iida-az1-p01-net01-any-icmp                   allow     icmp        test           jp-east-1a
fdae67e1-9f7f-47de-93af-23fad02ff59b  iida-az1-p01-net01-any-tcp                    allow     tcp         test           jp-east-1a
====================================  ================================  ==========  ========  ==========  =============  ===================
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
except ImportError:
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
def main(dump=False):
  """メイン関数"""

  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/fw/firewall_rules"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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
    return r

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

  keys = ['id', 'name', 'position', 'action', 'protocol', 'description', 'availability_zone']

  rules_list = []
  for item in data.get('firewall_rules', []):
    items = []
    rules_list.append(items)
    for key in keys:
      items.append(item.get(key, ''))

  # 一覧を表示
  print("/v2.0/fw/firewall_rules")
  print(tabulate(rules_list, headers=keys, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main():
    """メイン関数を実行します"""
    import argparse
    parser = argparse.ArgumentParser(description='Lists firewall rules.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump
    main(dump=dump)

  # 実行
  run_main()
