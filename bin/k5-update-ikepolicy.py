#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/vpn/ikepolicies/{ikepolicy-id}
Update IKE policy
IKEポリシーを更新する

NOTE:
　・設定ファイルが必要です $app_home/conf/ipsec.yaml
　・使用中のIKEポリシーは更新できないので、コネクションを削除すること
"""

"""
実行例

bash-4.4$ ./bin/k5-list-ikepolicy.py
GET /v2.0/vpn/ikepolicies
====================================  ==================  ================================  ===================
id                                    name                tenant_id                         availability_zone
====================================  ==================  ================================  ===================
9fc16042-95ae-46b9-84bc-4777b3b9f89c  iida-az1-ikepolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ==================  ================================  ===================


bash-4.4$ ./bin/k5-update-ikepolicy.py \
--policy-id 9fc16042-95ae-46b9-84bc-4777b3b9f89c \
--name iida-az1-ikepolicy

PUT /v2.0/vpn/ikepolicies/{ikepolicy-id}
=======================  ====================================
name                     iida-az1-ikepolicy
id                       9fc16042-95ae-46b9-84bc-4777b3b9f89c
auth_algorithm           sha1
pfs                      group14
ike_version              v1
encryption_algorithm     aes-256
phase1_negotiation_mode  main
tenant_id                a5001a8b9c4a4712985c11377bd6d4fe
availability_zone        jp-east-1a
=======================  ====================================
bash-4.4$
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


#
# リクエストデータを作成する
#
def make_request_data(config=None):
  """リクエストデータを作成して返却します"""

  data = config.get('ikepolicy', {})

  ikepolicy_object = {}

  allowed_keys = ['encryption_algorithm', 'pfs', 'lifetime', 'name', 'description']
  for key in allowed_keys:
    item = data.get(key, None)
    if item:
      ikepolicy_object[key] = data.get(key)

  return {'ikepolicy': ikepolicy_object}


#
# APIにアクセスする
#
def access_api(policy_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ikepolicies/" + policy_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで作成して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

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

  item = data.get('ikepolicy', {})

  disp_keys = [
    'name', 'id', 'auth_algorithm', 'pfs', 'ike_version', 'encryption_algorithm', 'phase1_negotiation_mode',
    'tenant_id', 'availability_zone'
  ]

  disp_list = []

  for key in disp_keys:
    row = []
    row.append(key)
    row.append(item.get(key, ''))
    disp_list.append(row)

  print("PUT /v2.0/vpn/ikepolicies/{ikepolicy-id}")
  print(tabulate(disp_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse
  import codecs
  import yaml

  def main():
    """メイン関数"""

    # アプリケーションのホームディレクトリ
    app_home = here("..")

    # デフォルトのコンフィグファイルの名前
    # $app_home/conf/ipsec.yaml
    config_file = os.path.join(app_home, "conf", "ipsec.yaml")

    parser = argparse.ArgumentParser(description='Updates an IKE policy.')
    parser.add_argument('--policy-id', dest='policy_id', metavar='id', required=True, help="The ike policy id.")
    parser.add_argument('--name', metavar='name', required=True, help='The name of the vpn service.')
    parser.add_argument('--filename', metavar='file', default=config_file, help='The configuration file. default: '+config_file)
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    policy_id = args.policy_id
    dump = args.dump

    if not os.path.exists(config_file):
      logging.error("Config file not found. %s", config_file)
      return 1

    with codecs.open(config_file, 'r', 'utf-8') as f:
      try:
        data = yaml.load(f)
      except yaml.YAMLError:
        logging.error("YAML error")
        return 1

    config = data.get(name, {})
    if not config:
      logging.error("name not found in the yaml file.")
      return 1

    request_data = make_request_data(config=config)

    # 実行
    result = access_api(policy_id=policy_id, data=request_data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
