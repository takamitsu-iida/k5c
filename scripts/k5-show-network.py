#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/networks/{network_id}
Show network
指定したネットワークの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network.py 93a83e0e-424e-4e7d-8299-4bdea906354e
GET /v2.0/networks/{network_id}
===================  ====================================  ==========  ========
name                 id                                    az          status
===================  ====================================  ==========  ========
iida-test-network-1  93a83e0e-424e-4e7d-8299-4bdea906354e  jp-east-1a  ACTIVE
===================  ====================================  ==========  ========

====================================
subnets
====================================
38701f66-4610-493f-9c15-78f81917f362
====================================
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
def main(network_id='', dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/networks/" + network_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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

  # ネットワーク情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
  nw = data.get('network', {})

  # ネットワーク情報を表示
  networks = []
  networks.append([nw.get('name', ''), nw.get('id', ''), nw.get('availability_zone', ''), nw.get('status', '')])
  print("GET /v2.0/networks/{network_id}")
  print(tabulate(networks, headers=['name', 'id', 'az', 'status'], tablefmt='rst'))

  # サブネット一覧を表示
  subnets_list = []
  for item in nw.get('subnets', []):
    subnets_list.append([item])
  print("")
  print(tabulate(subnets_list, headers=['subnets'], tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "network_id"))
    exit(1)

  main(network_id=sys.argv[1], dump=False)
