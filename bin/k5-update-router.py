#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}
Update router
指定したルータの情報を更新する

NOTE:
　・external_gateway_infoのみを更新します
　・一度external_gateway_infoを空っぽにしたあと、指定したexternal_gateway_infoを設定します
"""

"""
実行例

bash-4.4$ ./k5-update-router.py --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --network_id cd4057bd-f72e-4244-a7dd-1bcb2775dd67
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
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
def main(router_id="", network_id="", dump=False):
  """
  ルータの外部向けのネットワークを設定します。
  """
  # 接続先URL
  url = k5c.EP_NETWORK +  "/v2.0/routers/" + router_id

  # 設定する外部ネットワークの情報
  if network_id:
    router_object = {
      'router': {
        'external_gateway_info': {
          'network_id': network_id
        }
      }
    }
  else:
    router_object = {
      'router': {
        'external_gateway_info': None
      }
    }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッド
  r = c.put(url=url, data=router_object)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return r

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    # ステータスコードが503の場合は2分後に実行を促す
    if status_code == 503:
      print("\nNOTE:")
      print("External gateway is being configured. Please try it again about 2 minutes later.")
    return r

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    return r

  # 変更したルータの情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
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
  print("PUT /v2.0/routers/{router_id}")
  print(tabulate(rtrs, tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:

      # 対象ルータ
      # bash-4.4$ ./k5-list-routers.py
      # GET /v2.0/routers
      # ====================================  =================  ================================  ==========  ========
      # id                                    name               tenant_id                         az          status
      # ====================================  =================  ================================  ==========  ========
      # 05dbac99-4058-4f60-a9cc-a7593a681d7b  iida-ext-router-1  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
      # ====================================  =================  ================================  ==========  ========

      router_id = "05dbac99-4058-4f60-a9cc-a7593a681d7b"

      # 外部向けネットワーク
      # グローバルIPが枯渇しているとエラーになる
      # bash-4.4$ ./k5-list-networks.py | grep jp-east-1a
      # 6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
      # 92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
      # a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
      # af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
      # cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE

      network_id = "6d9df982-7a89-462a-8b17-8a8e5befa63e"  # inf_az1_ext-net03

      # jsonをダンプ
      dump = False

    else:
      import argparse
      parser = argparse.ArgumentParser(description='Updates a logical router.')
      parser.add_argument('--router_id', required=True, help='The router id.')
      parser.add_argument('--network_id', nargs='?', default='', required=True, help='The network_id, for the external gateway.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()

      router_id = args.router_id
      network_id = args.network_id
      dump = args.dump

    # まずはexternal_gateway_infoを空っぽにする
    main(router_id=router_id, network_id="", dump=dump)

    # 次にexternal_gateway_infoを設定する
    if network_id:
      main(router_id=router_id, network_id=network_id, dump=dump)

  # 実行
  run_main()
