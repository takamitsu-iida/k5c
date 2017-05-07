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

# 通常はWARN
# 多めに情報を見たい場合はINFO
logging.basicConfig(level=logging.WARN)

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.error("k5cモジュールのインポートに失敗しました")
  logging.error(e)
  exit(1)

try:
  from k5c import k5config  # need info in k5config.py
except ImportError:
  logging.error("k5configモジュールの読み込みに失敗しました。")
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.error("tabulateモジュールのインポートに失敗しました")
  exit(1)

#
# メイン
#
def main(name="", az="", dump=False):
  """
  ネットワークを作成します。
  """
  # 接続先URL
  url = k5config.URL_NETWORKS

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
  # 作成するネットワークの名前
  # name = "iida-test-network-1"

  # 作成する場所
  # az = "jp-east-1a"

  # 実行
  main(name="iida-test-network-1", az="jp-east-1a", dump=False)
