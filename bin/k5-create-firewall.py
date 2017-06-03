#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/fw/firewalls
Create firewall
ファイアーウォールを作成する
"""

"""
実行例

bash-4.4$ ./bin/k5-create-firewall.py --name fw1 \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--policy-id b851c88d-ca26-4218-9b9a-75490708f0df

/v2.0/fw/firewalls
==================  ====================================
id                  2a323a21-23fc-4ec7-86d3-e1f900ba6876
name                fw1
router_id           ffbd70be-24cf-4dff-a4f6-661bf892e313
firewall_policy_id  b851c88d-ca26-4218-9b9a-75490708f0df
status              PENDING_CREATE
availability_zone   jp-east-1a
tenant_id           a5001a8b9c4a4712985c11377bd6d4fe
==================  ====================================
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
# リクエストデータを作成
#
def make_request_data(name="", policy_id="", router_id="", az=""):
  """リクエストデータを作成して返却します"""

  firewall_object = {}

  if name:
    firewall_object['name'] = name

  if policy_id:
    firewall_object['firewall_policy_id'] = policy_id

  if router_id:
    firewall_object['router_id'] = router_id

  if az:
    firewall_object['availability_zone'] = az

  # 作成するルールのオブジェクト
  request_data = {
    'firewall': firewall_object
  }

  return request_data


#
# APIにアクセス
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/fw/firewalls"

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

  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 201,
  #  "data": {
  #    "firewall": {
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "name": "r1",
  #      "availability_zone": "jp-east-1a",
  #      "id": "9e4e0615-92fd-4832-9316-850cfeb0004f",
  #      "admin_state_up": true,
  #      "firewall_policy_id": "b851c88d-ca26-4218-9b9a-75490708f0df",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313",
  #      "status": "PENDING_CREATE",
  #      "description": ""
  #    }
  #  }
  #}
  fw = data.get('firewall', {})

  # 表示用に配列にする
  disp_keys = [
    'id', 'name', 'router_id', 'firewall_policy_id', 'status', 'availability_zone', 'tenant_id'
  ]

  disp_list = []
  for key in disp_keys:
    disp_list.append([key, fw.get(key, '')])

  print("/v2.0/fw/firewalls")
  print(tabulate(disp_list, tablefmt='rst'))


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

    parser = argparse.ArgumentParser(description='Creates a firewall.')
    parser.add_argument('--policy-id', dest='policy_id', metavar='id', required=True, help='The firewall policy uuid that this firewall is associated with.')
    parser.add_argument('--router-id', dest='router_id', metavar='id', required=True, help='The ID of the router that this firewall be applied.')
    parser.add_argument('--name', metavar='name', required=True, help='Human readable name for the firewall')
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    policy_id = args.policy_id
    router_id = args.router_id
    name = args.name
    az = args.az
    dump = args.dump

    data = make_request_data(name=name, policy_id=policy_id, router_id=router_id, az=az)
    # print(json.dumps(data, indent=2))

    # 実行
    result = access_api(data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result=result)

    return 0


  # 実行
  sys.exit(main())
