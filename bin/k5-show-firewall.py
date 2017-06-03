#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/fw/firewalls/{firewall-id}
Shows firewall details.
ファイアーウォールの詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-firewalls.py | ./bin/k5-show-firewall.py -
firewall_id: 94b21ac8-1890-417a-a2de-515ec0a009d6
GET /v2.0/fw/firewalls/{firewall-id}
==================  ====================================
id                  94b21ac8-1890-417a-a2de-515ec0a009d6
name                iida-az1-fw01
router_id           ffbd70be-24cf-4dff-a4f6-661bf892e313
firewall_policy_id  3e500de7-5d7c-4585-954f-f911e077fa58
status              ACTIVE
availability_zone   jp-east-1a
tenant_id           a5001a8b9c4a4712985c11377bd6d4fe
==================  ====================================
"""

import json
import logging
import os
import sys

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  if getattr(sys, 'frozen', False):
    # cx_Freezeで固めた場合は実行ファイルからの相対パス
    return os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
  else:
    # 通常はこのファイルの場所からの相対パス
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
def access_api(firewall_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/fw/firewalls/" + firewall_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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

  #{
  #  "status_code": 200,
  #  "data": {
  #    "firewall": {
  #      "description": "",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #      "firewall_policy_id": "3e500de7-5d7c-4585-954f-f911e077fa58",
  #      "id": "94b21ac8-1890-417a-a2de-515ec0a009d6",
  #      "admin_state_up": true,
  #      "status": "ACTIVE",
  #      "availability_zone": "jp-east-1a",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "name": "iida-az1-fw01"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8"
  #}

  fw = data.get('firewall', {})

  # 表示用に配列にする
  disp_keys = [
    'id', 'name', 'router_id', 'firewall_policy_id', 'status', 'availability_zone', 'tenant_id'
  ]

  disp_list = []
  for key in disp_keys:
    disp_list.append([key, fw.get(key, '')])

  print("GET /v2.0/fw/firewalls/{firewall-id}")
  print(tabulate(disp_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows firewall details.')
    parser.add_argument('firewall_id', metavar='id', help='The firewall id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    firewall_id = args.firewall_id
    dump = args.dump

    if firewall_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(firewall_id=uuid)
          print("firewall_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(firewall_id=firewall_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
