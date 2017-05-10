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
bash-4.4$ ./k5-create-network.py
POST /v2.0/networks
=========  ====================================
name       iida-test-network-1
id         93a83e0e-424e-4e7d-8299-4bdea906354e
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
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  exit(1)

try:
  from k5c import k5config  # need info in k5config.py
except ImportError as e:
  logging.exception("k5configモジュールの読み込みに失敗しました: %s", e)
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(name="", az="", dump=False):
  """
  ネットワークを作成します。
  """
  # 接続先URL
  url = k5config.EP_NETWORK + "/v2.0/networks"

  # 作成するネットワークのオブジェクト
  network_object = {
    'network': {
      'name': name,
      'availability_zone': az
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=network_object)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return r

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    return r

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    return r

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

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:
      # 作成するネットワークの名前
      name = "iida-test-network-1"

      # 作成する場所
      az = "jp-east-1a"

      # jsonをダンプ
      dump = False

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Create network.')
      parser.add_argument('--name', required=True, help='The network name.')
      parser.add_argument('--az', required=True, help='The Availability Zone name.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      name = args.name
      az = args.az
      dump = args.dump

    main(name=name, az=az, dump=dump)

  # 実行
  run_main()
