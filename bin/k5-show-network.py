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
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(network_id='', dump=False):
  """メイン関数"""
  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/networks/" + network_id

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

  def run_main():
    """メイン関数を実行します"""
    import argparse
    parser = argparse.ArgumentParser(description='Shows information for a specified network.')
    parser.add_argument('network_id', help='Network id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    network_id = args.network_id
    dump = args.dump
    main(network_id=network_id, dump=dump)

  # 実行
  run_main()
