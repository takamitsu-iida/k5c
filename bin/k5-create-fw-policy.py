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

  # 作成したポリシーの情報はデータオブジェクトの中の'firewall_policy'キーにオブジェクトとして入っている
  #"data": {
  #  "firewall_policy": {
  #    "id": "84417ab6-53ea-4595-9d92-7a9d9a552e12",
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "firewall_rules": [
  #      "867e35c5-2875-4c51-af31-4cf7932f17f6",
  #      "9597ea56-e39d-4160-bdca-ebf2aca23aab",
  #      "589d96ad-79e9-4a84-b923-10145469643c",
  #      "c44321b7-6b04-4ec4-8e62-dc080794f59b",
  #      "57fbe4aa-6edf-4123-8b6c-c8233cfb3c70",
  #      "6eb8b10f-0756-460a-8b6a-8dd3db77173d",
  #      "58dfdc2f-bf23-481b-9f3a-4b96df6232a2",
  #      "75877f59-7a26-4a59-a343-9e2955dfb49e",
  #      "8cf91195-d611-489d-b322-e28cab2ba705",
  #      "acfada3d-0527-43e7-ba4d-6403ca8654fe",
  #      "3750f08f-5567-4ad7-870f-dd830cc898b0",
  #      "bc8f66e6-c09c-448f-869c-96f2c0843e81"
  #    ],  #    "description": "",
  #    "availability_zone": "jp-east-1a",
  #    "shared": false,
  #    "name": "iida",
  #    "audited": false
  #  }
  #},
  fp = data.get('firewall_policy', {})

  # 表示用に配列にする
  disp_keys = ['id', 'name', 'availability_zone', 'tenant_id']
  fps = []
  for key in disp_keys:
    fps.append([key, fp.get(key, '')])

  # ファイアウォールポリシー情報を表示
  print("POST /v2.0/fw/firewall_policies")
  print(tabulate(fps, tablefmt='rst'))

  # ルール一覧を表示
  rules = []
  for item in fp.get('firewall_rules', []):
    rules.append([item])
  print(tabulate(rules, tablefmt='rst'))


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
    data = make_request_data(name=name, rule_id_list=rule_id_list, az=az)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(data=data)

    # 得たデータを処理する
    print_result(result=result, dump=dump)

    # 結果をエクセルに書く
    if save:
      policy_id = get_policy_id(result)
      fwcommon.save_policy(filename=filename, rule_id_list=rule_id_list, policy_id=policy_id)

    return 0


  # 実行
  sys.exit(main())
