#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/network_connector_endpoints/{network connector endpoint id}/disconnect
Disconnect Network Connector Endpoint
ネットワークコネクタエンドポイントからインターフェイスを接続解除する

NOTE:
　・実行するとポートそのものが削除されてしまいます！
"""

"""
実行例

bash-4.4$ ./k5-disconnect-network-connector-endpoint.py
status_code: 200
{'interface': {'port_id': '863f2404-4a92-4991-8fab-e4312682dd86'}}
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

#
# メイン
#
def main(ncep_id="", port_id="", dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id + "/disconnect"

  # 切断対象となるインタフェースのオブジェクト
  interface_object = {
    'interface' : {
      'port_id' : port_id
    }
  }

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=interface_object)

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

  # 結果表示
  print("status_code: {0}".format(r.get('status_code', "")))
  print(r.get('data', ""))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main(DEBUG=False):
    """メイン関数を呼び出します"""
    if DEBUG:
      # 対象のコネクタエンドポイントID
      ncep_id = "ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"

      # 切断するポートID
      port_id = "863f2404-4a92-4991-8fab-e4312682dd86"

      # jsonをダンプ
      dump = False
    else:
      import argparse
      parser = argparse.ArgumentParser(description='Disconnect interface to a specified network connector endpoint.')
      parser.add_argument('--ncep_id', required=True, help='Network connector endpoint id.')
      parser.add_argument('--port_id', required=True, help='Port id.')
      parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
      args = parser.parse_args()
      ncep_id = args.ncep_id
      port_id = args.port_id
      dump = args.dump

    main(ncep_id=ncep_id, port_id=port_id, dump=dump)

  # 実行
  run_main()
