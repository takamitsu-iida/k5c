#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/networks
Create network
ネットワークを作成する

注意：
　・作成するネットワークの名前とゾーンはスクリプトのmain()で指定
　・同じ名前であっても何個でも作れる（idで区別）
"""

"""
実行例

bash-4.4$ ./k5-create-network.py
POST /v2.0/networks
=========  ====================================
name       iida-test-network
id         acb539fc-4a5d-4fc3-bc70-324ee336d587
az         jp-east-1b
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
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
  url = k5config.URL_NETWORK

  # 作成するネットワークの名前
  name = "iida-test-network"

  # 作成する場所
  az = "jp-east-1b"

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
    return

  # 戻り値は'status_code'キーに格納
  # ステータスコードが負の場合は、何かおかしかったということ
  if r.get('status_code', -1) < 0:
    logging.error("failed to POST %s", url)
    exit(1)

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    exit(1)

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
  print('POST /v2.0/networks')
  print(tabulate(nws, tablefmt='rst'))


if __name__ == '__main__':
  main(dump=False)
