#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/fw/firewall_policies/{firewall_policy_id}
Update firewall policy
ファイアーウォールポリシーを更新する

NOTE:
　・ルールはエクセルで作成します
　・ルールファイルのデフォルトのファイル名は$app_home/conf/fw-rules.xlsxです
　・エクセル内の同じidのルールを変更します
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

try:
  import fwcommon
except ImportError as e:
  logging.exception("fwcommon.pyのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# リクエストデータを作成
#
def make_request_data(rule=None):
  """リクエストデータを作成して返却します"""
  if not rule:
    return None

  # 作成するルールのオブジェクト
  request_data = {
    'firewall_rule': rule
  }

  return request_data


#
# APIにアクセス
#
def access_api(rule_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_rules/" + rule_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで更新
  r = c.put(url=url, data=data)

  return r


#
# 結果を表示
#
def print_result(result=None, dump=False):
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

  # 作成したルールの情報はデータオブジェクトの中の'firewall_rule'キーにオブジェクトとして入っている
  #"data": {
  #  "firewall_rule": {
  #    "destination_ip_address": null,
  #    "action": "allow",
  #    "ip_version": 4,
  #    "firewall_policy_id": null,
  #    "position": null,
  #    "source_ip_address": "133.162.192.0/24",
  #    "id": "de2bb711-d495-4ae5-9d05-672575d1549a",
  #    "shared": false,
  #    "availability_zone": "jp-east-1a",
  #    "destination_port": null,
  #    "enabled": true,
  #    "protocol": "tcp",
  #    "description": "",
  #    "name": "iida-az1-p01-mgmt01-any-tcp",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "source_port": null
  #  }
  #}
  rule = data.get('firewall_rule', {})

  # 表示用に配列にする
  rules = []
  rule_id = rule.get('id', '')
  rules.append(['id', rule_id])
  rules.append(['name', rule.get('name', '')])
  rules.append(['enabled', rule.get('enabled', '')])
  rules.append(['action', rule.get('action', '')])
  rules.append(['protocol', rule.get('protocol', '')])
  rules.append(['source_ip_address', rule.get('source_ip_address', '')])
  rules.append(['source_port', rule.get('source_port', '')])
  rules.append(['destination_ip_address', rule.get('destination_ip_address', '')])
  rules.append(['destination_port', rule.get('destination_port', '')])
  rules.append(['description', rule.get('description', '')])
  rules.append(['availability_zone', rule.get('availability_zone', '')])
  rules.append(['tenant_id', rule.get('tenant_id', '')])

  # ファイアウォールルール情報を表示
  print("PUT /v2.0/fw/firewall_policies/{firewall_policy_id}")
  print(tabulate(rules, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # 設定ファイルのパス
    # $app_home/conf/fw-rules.xlsx
    config_file = os.path.join(app_home, "conf", "fw-rules.xlsx")

    parser = argparse.ArgumentParser(description='Updates a firewall rule.')
    parser.add_argument('rule_id', metavar='id', help='The firewall rule id.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The rule file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    rule_id = args.rule_id
    filename = args.filename
    dump = args.dump

    if rule_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          rule = fwcommon.get_rule_to_update(filename=filename, rule_id=uuid)
          if not rule:
            print("no rule found for {}".format(uuid))
            continue
          data = make_request_data(rule)
          result = access_api(rule_id=uuid, data=data)
          print_result(result, dump=dump)
          print("")
          sys.stdout.flush()
      return 0

    # ファイルからルールを読み取ってリクエストデータを作る
    rule = fwcommon.get_rule_to_update(filename=filename, rule_id=rule_id)

    if not rule:
      print("no rule found for {}".format(rule_id))
      return 1

    # リクエストデータを作成
    data = make_request_data(rule)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(rule_id=rule_id, data=data)

    # 表示
    print_result(result=result, dump=dump)

    return 0


  # 実行
  sys.exit(main())
