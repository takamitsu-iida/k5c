#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/fw/firewall_policies
Create firewall policy
ファイアーウォールポリシーを作成する

NOTE:
　・ルールはエクセルで作成します
　・ルールファイルのデフォルトのファイル名は$app_home/conf/fw-rules.xlsxです
　・エクセルに記載の順に作成します
　・idの記載がないルールは無視されます
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
  import fwcommon
except ImportError as e:
  logging.exception("fwcommon.pyのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# リクエストデータを作成
#
def make_request_data(name="", rule_id_list=None, az=""):
  """リクエストデータを作成して返却します"""

  policy_object = {
    'name': name
  }

  if rule_id_list:
    policy_object['firewall_rules'] = rule_id_list

  if az:
    policy_object['availability_zone'] = az

  # 作成するルールのオブジェクト
  request_data = {
    'firewall_policy': policy_object
  }

  return request_data


#
# APIにアクセス
#
def access_api(data=None):
  """REST APIにアクセスします"""
  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_policies"

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

  fwcommon.print_fw_policy(data)


def get_policy_id(result=None):
  """firewall_policy_idを探して返却します"""
  data = result.get('data', None)
  if not data:
    return None
  policy = data.get('firewall_policy', {})
  return policy.get('id', '')


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # 設定ファイルのパス
    # $app_home/conf/fw-rules.xlsx
    config_file = os.path.join(app_home, "conf", "fw-rules.xlsx")

    parser = argparse.ArgumentParser(description='Creates a firewall policy.')
    parser.add_argument('--name', metavar='name', required=True, help='The rule name.')
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--filename', metavar='file', default=config_file, help='The rule file. default: '+config_file)
    parser.add_argument('--save', action='store_true', default=False, help='Write policy-id to excel file.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    az = args.az
    filename = args.filename
    save = args.save
    dump = args.dump

    # ファイルからルールIDの配列を読み取る
    rule_id_list = fwcommon.get_rule_id_list(filename=filename)
    if not rule_id_list:
      logging.error("no rule found.")
      return 1

    data = make_request_data(name=name, rule_id_list=rule_id_list, az=az)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result=result)

    # 結果をエクセルに書く
    if save:
      policy_id = get_policy_id(result)
      fwcommon.save_policy(filename=filename, rule_id_list=rule_id_list, policy_id=policy_id, policy_name=name)

    return 0


  # 実行
  sys.exit(main())
