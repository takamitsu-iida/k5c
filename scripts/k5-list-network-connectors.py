#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/network_connectors
List Network Connectors
ネットワークコネクタの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-network-connectors.py
GET /v2.0/network_connectors
====================================  ============================  ====================================  ================================
id                                    name                          pool_id                               tenant_id
====================================  ============================  ====================================  ================================
d6901be5-bbab-4194-ae21-1eb78822aacb  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
1dc0c2a3-d3ce-4b66-bc8d-888566270435  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
6ce8674b-dde8-4262-9e2a-b19ee06634f1  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
5e35b8cc-c0a1-434b-a7f3-b5f9218665eb  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
9ec0ed5e-7a51-4164-b506-be79e59eab6d  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
348a2574-7323-407f-b23d-b1ac78200a47  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
aff51cdb-a3d4-43e3-95b9-137e73e8767f  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
385bc7f5-bcc4-4521-ad41-de2074143355  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e  a5001a8b9c4a4712985c11377bd6d4fe
====================================  ============================  ====================================  ================================
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
def main(dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.URL_NETWORK_CONNECTORS

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return

  # 戻り値は'status_code'キーに格納
  # ステータスコードが負の場合は、何かおかしかったということ
  if r.get('status_code', -1) < 0:
    logging.error("failed to GET %s", url)
    exit(1)

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    exit(1)

  # ネットワークコネクタ一覧はデータオブジェクトの中の'network_connectors'キーに配列として入っている
  nc_list = []
  for item in data.get('network_connectors', []):
    nc_list.append([item.get('id', ''), item.get('name', ''), item.get('network_connector_pool_id', ''), item.get('tenant_id', '')])

  # ユーザ一覧を表示
  print('GET /v2.0/network_connectors')
  print(tabulate(nc_list, headers=['id', 'name', 'pool_id', 'tenant_id'], tablefmt='rst'))


if __name__ == '__main__':
  main(dump=False)
