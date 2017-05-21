#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/fw/firewall_rules
Create firewall rule
ファイアーウォールのルールを作成する

NOTE:
　・ルールはエクセルで作成します
　・ルールファイルのデフォルトのファイル名は$app_home/conf/fw-rules.xlsxです
　・エクセル内の同じ名前のルールを作成します
　・ルールの作成に成功すると、得られたIDをエクセルファイルに追記します
"""

"""
実行例

bash-4.4$ ./k5-create-fw-rule.py --name iida-az1-p01-mgmt01-any-tcp
POST /v2.0/fw/firewall_rules
======================  ====================================
id                      04f9bbc2-34f3-4b88-8313-def1f6984a9a
name                    iida-az1-p01-mgmt01-any-tcp
enabled                 True
action                  allow
protocol                tcp
source_ip_address       192.168.246.0/24
source_port
destination_ip_address
destination_port
description             test
availability_zone       jp-east-1a
tenant_id               a5001a8b9c4a4712985c11377bd6d4fe
======================  ====================================
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
def access_api(data=None):
  """REST APIにアクセスします"""
  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_rules"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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
  print("POST /v2.0/fw/firewall_rules")
  print(tabulate(rules, tablefmt='rst'))


def get_rule_id(result=None):
  """REST APIからの戻り値からrule_idを探して返却します"""
  data = result.get('data', None)
  if not data:
    return None
  rule = data.get('firewall_rule', {})
  return rule.get('id', '')


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # 設定ファイルのパス
    # $app_home/conf/fw-rules.xlsx
    config_file = os.path.join(app_home, "conf", "fw-rules.xlsx")

    parser = argparse.ArgumentParser(description='Creates a firewall rule.')
    parser.add_argument('--name', metavar='name', required=True, help='The rule name.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The rule file. default: '+config_file)
    parser.add_argument('--save', action='store_true', default=False, help='Write rule-id to the excel file.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    filename = args.filename
    save = args.save
    dump = args.dump

    # エクセルファイルからIDが空白のルールを全て取り出す
    rules = fwcommon.get_rules_to_create(filename=filename)
    if not rules:
      logging.error("no rule found.")
      return 1

    # 順に処理
    for rule in rules:
      if name == 'all' or name == rule.get('name', ""):
        data = make_request_data(rule)
        if not data:
          continue

        # 実行
        result = access_api(data=data)

        # 中身を確認
        if dump:
          print(json.dumps(result, indent=2))
          return 0

        # 表示
        print_result(result=result)
        print("")
        sys.stdout.flush()

        # 結果をエクセルに書く
        if save:
          rule_id = get_rule_id(result)
          fwcommon.save_rule(filename=filename, name=rule.get('name', ""), rule_id=rule_id)

    return 0


  # 実行
  sys.exit(main())
