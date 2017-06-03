#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/ipsecpolicies/{ipsecpolicyid}
Show IPSec policy details
指定した IPsecポリシーの詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-ipsecpolicy.py | ./bin/k5-show-ipsecpolicy.py -
ipsecpolicy_id: ab659e26-327b-4aff-b727-b039da09f22e
GET /v2.0/vpn/ipsecpolicies/{ipsecpolicy-id}
====================  ====================================
name                  iida-az1-ipsecpolicy
id                    ab659e26-327b-4aff-b727-b039da09f22e
pfs                   group14
auth_algorithm        sha1
encryption_algorithm  aes-256
transform_protocol    esp
tenant_id             a5001a8b9c4a4712985c11377bd6d4fe
availability_zone     jp-east-1a
====================  ====================================

lifetime
=====  =======
value  28800
units  seconds
=====  =======

bash-4.4$
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
def access_api(ipsecpolicy_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsecpolicies/" + ipsecpolicy_id

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
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": {
  #    "ipsecpolicy": {
  #      "auth_algorithm": "sha1",
  #      "encapsulation_mode": "tunnel",
  #      "lifetime": {
  #        "value": 28800,
  #        "units": "seconds"
  #      },
  #      "description": "",
  #      "transform_protocol": "esp",
  #      "name": "iida-az1-ipsecpolicy",
  #      "availability_zone": "jp-east-1a",
  #      "pfs": "group14",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "encryption_algorithm": "aes-256",
  #      "id": "26525271-0337-4ad2-b0d3-120814fc0794"
  #    }
  #  },
  #  "status_code": 200
  #}

  item = data.get('ipsecpolicy', {})

  disp_keys = [
    'name', 'id', 'pfs', 'auth_algorithm', 'encryption_algorithm', 'transform_protocol',
    'tenant_id', 'availability_zone'
  ]

  disp_list = []

  for key in disp_keys:
    row = []
    row.append(key)
    row.append(item.get(key, ''))
    disp_list.append(row)

  print("GET /v2.0/vpn/ipsecpolicies/{ipsecpolicy-id}")
  print(tabulate(disp_list, tablefmt='rst'))

  lifetime = item.get('lifetime', {})
  lifetime_list = []
  lifetime_keys = ['value', 'units']
  for key in lifetime_keys:
    row = []
    row.append(key)
    row.append(lifetime.get(key, ''))
    lifetime_list.append(row)

  print("")
  print("lifetime")
  print(tabulate(lifetime_list, tablefmt='rst'))



if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows details for a specified IKE policy.')
    parser.add_argument('ipsecpolicy_id', metavar='id', help='The ikepolicy id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    ipsecpolicy_id = args.ipsecpolicy_id
    dump = args.dump

    if ipsecpolicy_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(ipsecpolicy_id=uuid)
          print("ipsecpolicy_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0


    # 実行
    result = access_api(ipsecpolicy_id=ipsecpolicy_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
