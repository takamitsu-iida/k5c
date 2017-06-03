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
def make_request_data(name="", rule_id_list=None):
  """リクエストデータを作成して返却します"""

  policy_object = {}

  if name:
    policy_object['name'] = name

  if rule_id_list is not None:
    policy_object['firewall_rules'] = rule_id_list

  # 作成するルールのオブジェクト
  request_data = {
    'firewall_policy': policy_object
  }

  return request_data


#
# APIにアクセス
#
def access_api(policy_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_policies/" + policy_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
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

  fwcommon.print_fw_policy(data=data)


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

    parser = argparse.ArgumentParser(description='Updates a firewall policy.')
    parser.add_argument('policy_id', metavar='id', help='The firewall policy id.')
    parser.add_argument('--name', metavar='name', help='The rule name.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The rule file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    policy_id = args.policy_id
    name = args.name
    filename = args.filename
    dump = args.dump

    # ファイルからルールIDの配列を読み取る
    rule_id_list = fwcommon.get_policy_rules_to_update(filename=filename, policy_id=policy_id)
    if rule_id_list is None:
      print("no policy found for {}".format(policy_id))
      return 1

    # リクエストデータを作る
    data = make_request_data(name=name, rule_id_list=rule_id_list)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(policy_id=policy_id, data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result=result)

    return 0


  # 実行
  sys.exit(main())
