#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/routers
Create router
論理ルータを作成する

NOTE:
"""

"""
実行例

bash-4.4$ ./k5-create-router.py
POST /v2.0/routers
==============  ====================================
name            iida-test-router-1
id              5359cce0-cd5c-48e8-891a-659c5ae62f65
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
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
  url = k5config.EP_NETWORK +  "/v2.0/routers"

  # 作成するルータの情報
  router_object = {
    'router': {
      'name': name,
      'admin_state_up': True,
      'availability_zone': az
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=router_object)

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
  #"data": {
  #  "router": {
  #    "admin_state_up": true,
  #    "id": "ad3ddc47-6303-48e8-87ad-cb0333c93112",
  #    "name": "iida-test-router-1",
  #    "external_gateway_info": null,
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "status": "ACTIVE",
  #    "availability_zone": "jp-east-1a"
  #  }
  #}
  rtr = data.get('router', {})

  # 表示用に配列にする
  rtrs = []
  rtrs.append(['name', rtr.get('name', '')])
  rtrs.append(['id', rtr.get('id', '')])
  rtrs.append(['az', rtr.get('availability_zone', '')])
  rtrs.append(['tenant_id', rtr.get('tenant_id', '')])
  rtrs.append(['status', rtr.get('status', '')])
  rtrs.append(['admin_state_up', rtr.get('admin_state_up', '')])

  # 表示
  print("POST /v2.0/routers")
  print(tabulate(rtrs, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  # 実行
  main(name="iida-test-router-1", az="jp-east-1a", dump=False)
