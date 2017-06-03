#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/fw/firewall_rules/{firewall_rule_id}
Update firewall rule
ファイアーウォールのルールを更新する

NOTE:
　・ルールはエクセルで作成します
　・ルールファイルのデフォルトのファイル名は$app_home/conf/fw-rules.xlsxです
　・エクセル内の同じidのルールを変更します
"""

"""
実行例

bash-4.4$ ./bin/k5-update-fw-rule.py --rule-id 2b9a71f6-6885-460e-a1a4-32e84c126a0e
PUT /v2.0/fw/firewall_rules
======================  ====================================
id                      2b9a71f6-6885-460e-a1a4-32e84c126a0e
name                    iida-az1-p01-net02-any-tcp
enabled                 True
action                  allow
protocol                tcp
source_ip_address       10.1.2.0/24
source_port
destination_ip_address
destination_port
description
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

  fwcommon.print_fw_rule(data)


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
          print_result(result)
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

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result=result)

    return 0


  # 実行
  sys.exit(main())
