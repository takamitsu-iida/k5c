#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/vpn/ipsecpolicies/{ipsecpolicyid}
Update IPSec Policy
IPsecポリシーを更新する

NOTE:
　・設定ファイルが必要です $app_home/conf/ipsec.yaml
"""

"""
実行例

bash-4.4$ ./bin/k5-list-ipsecpolicy.py
GET /v2.0/vpn/ipsecpolicies
====================================  ====================  ================================  ===================
id                                    name                  tenant_id                         availability_zone
====================================  ====================  ================================  ===================
26525271-0337-4ad2-b0d3-120814fc0794  iida-az1-ipsecpolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ====================  ================================  ===================

bash-4.4$ ./bin/k5-update-ipsecpolicy.py \
--policy-id 26525271-0337-4ad2-b0d3-120814fc0794 \
--name iida-az1-ipsecpolicy

PUT /v2.0/vpn/ikepolicies/{ikepolicy-id}
====================  ====================================
name                  iida-az1-ipsecpolicy
id                    26525271-0337-4ad2-b0d3-120814fc0794
pfs                   group14
auth_algorithm        sha1
encryption_algorithm  aes-256
transform_protocol    esp
tenant_id             a5001a8b9c4a4712985c11377bd6d4fe
availability_zone     jp-east-1a
====================  ====================================
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
# リクエストデータを作成する
#
def make_request_data(config=None):
  """リクエストデータを作成して返却します"""

  data = config.get('ipsecpolicy', {})

  ipsecpolicy_object = {}

  allowed_keys = ['name', 'encryption_algorithm', 'pfs', 'lifetime', 'description']

  for key in allowed_keys:
    item = data.get(key, None)
    if item:
      ipsecpolicy_object[key] = data.get(key)

  return {'ipsecpolicy': ipsecpolicy_object}


#
# APIにアクセスする
#
def access_api(policy_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ipsecpolicies/" + policy_id

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
