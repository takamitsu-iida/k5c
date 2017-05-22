#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/fw/firewall_policies/{firewall_policy_id}
Shows firewall policy details.
ファイアーウォールポリシーの詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-fw-policies.py | ./bin/k5-show-fw-policy.py -
b851c88d-ca26-4218-9b9a-75490708f0df
/v2.0/fw/firewall_policies
=================  ====================================
id                 b851c88d-ca26-4218-9b9a-75490708f0df
name               p1
availability_zone  jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
=================  ====================================
====================================
114d70cc-3c3c-4e17-a85c-fa995a084f44
1d048151-593e-4c16-87cc-ba37fb55a811
1583ce48-608c-429e-92cf-a82471929111
f89e509f-9cea-4587-bba6-63163ab41c73
79ca78c3-6905-4dde-9ff2-e26c1f9091e0
21fc602c-5aa1-4bdd-b145-7f4872e7e470
a9e5141a-8b29-408c-98c6-c64efb2437de
29ad528b-f868-49ee-bc84-6034f960dcba
07773c9a-6dd9-45f4-8722-ddfbf2981515
8bd856d6-1ee1-4402-a69b-65c3381d5c26
cf17f5bf-398e-4602-937d-a4da6b07a162
3158c601-4ce7-40ef-9efa-cee09968951e
====================================
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
  import fwcommon
except ImportError as e:
  logging.exception("fwcommon.pyのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# APIにアクセスする
#
def access_api(policy_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_policies/" + policy_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  return r


#
# 結果を表示
#
def print_result(result=None):
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

  fwcommon.print_fw_policy(data)


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows firewall policy details.')
    parser.add_argument('policy_id', metavar='policy-id', help='The firewall policy id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    policy_id = args.policy_id
    dump = args.dump

    if policy_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          # 実行
          result = access_api(policy_id=uuid)
          # 表示
          print(uuid)
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(policy_id=policy_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result=result)

    return 0


  # 実行
  sys.exit(main())
