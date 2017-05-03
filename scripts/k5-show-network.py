#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/networks/{network_id}
Show network
指定したネットワークの情報を表示する
"""

"""
実行例

bash-4.4$ ./k5-show-network.py 375c49fa-a706-4676-b55b-2d3554e5db6a
GET /v2.0/networks/{network_id}
=================  ====================================  ==========  ========
id                 name                                  az          status
=================  ====================================  ==========  ========
inf_az2_ext-net01  375c49fa-a706-4676-b55b-2d3554e5db6a  jp-east-1b  ACTIVE
=================  ====================================  ==========  ========

====================================
subnets
====================================
5079f324-5db0-44ee-92ac-3a6b7977b23f
a56b6058-0479-43a1-8b27-01c1c05e96a2
c1da3ee7-51c3-4801-bb97-aa03a4383ef0
e96e55b8-84bb-4777-a782-a5d6e8340039
f5e9ec37-88ec-494b-ac55-dae101a54cc1
====================================
bash-4.4$
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
  url = k5config.URL_NETWORK + "/" + network_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return

  # 戻り値は'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードがおかしい場合
  if status_code < 0 or status_code >= 300:
    print("status_code: {0}".format(r.get('status_code', "")))
    print(r.get('data', ""))
    exit(1)

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    exit(1)

  # ネットワーク情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
  nw = data.get('network', {})

  # ネットワーク情報を表示
  networks = []
  networks.append([nw.get('name', ''), nw.get('id', ''), nw.get('availability_zone', ''), nw.get('status', '')])
  print('GET /v2.0/networks/{network_id}')
  print(tabulate(networks, headers=['id', 'name', 'az', 'status'], tablefmt='rst'))

  # サブネット一覧を表示
  subnets_list = []
  for item in nw.get('subnets', []):
    subnets_list.append([item])
  print('')
  print(tabulate(subnets_list, headers=['subnets'], tablefmt='rst'))


if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "network_id"))
    exit(1)

  main(network_id=sys.argv[1], dump=False)
