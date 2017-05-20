#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/networks
Create network
ネットワークを作成する

NOTE:
　・作成するネットワークの名前とAvailability Zoneはスクリプト内に記述
　・同じ名前であっても何個でも作れる（idで区別）
"""

"""
実行例

bash-4.4$ ./bin/k5-create-network.py --name iida-az1-net03
POST /v2.0/networks
=========  ====================================
name       iida-az1-net03
id         01158253-4c9c-4cf5-b228-dc3a715b5c0b
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
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
def make_request_data(name="", az=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  # 作成するネットワークのオブジェクト
  network_object = {
    'network': {
      'name': name,
      'availability_zone': az
    }
  }

  return network_object


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/networks"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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

  # 作成したネットワークの情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
  nw = data.get('network', {})

  # 表示用に配列にする
  nws = []
  nws.append(['name', nw.get('name', '')])
  nws.append(['id', nw.get('id', '')])
  nws.append(['az', nw.get('availability_zone', '')])
  nws.append(['tenant_id', nw.get('tenant_id', '')])
  nws.append(['status', nw.get('status', '')])

  # ネットワーク情報を表示
  print("POST /v2.0/networks")
  print(tabulate(nws, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Create a network.')
    parser.add_argument('--name', metavar='name', required=True, help='The network name.')
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    name = args.name
    az = args.az
    dump = args.dump

    # 作成するネットワークの名前
    # name = "iida-test-network-1"
    #
    # 作成する場所
    # az = "jp-east-1a"
    #
    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(name=name, az=az)

    # 実行
    result = access_api(data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 得たデータを処理する
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
