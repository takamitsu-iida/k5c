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
if not here("../lib") in sys.path:
  sys.path.append(here("../lib"))

if not here("../lib/site-packages") in sys.path:
  sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# リクエストデータを作成する
#
def make_request_data(port_id=""):
  """リクエストデータを作成して返却します"""

  # 切断対象となるインタフェースのオブジェクト
  interface_object = {
    'interface' : {
      'port_id' : port_id
    }
  }

  return interface_object


#
# APIにアクセスする
#
def access_api(ncep_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id + "/disconnect"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

  return r


#
# 結果を表示する
#
def print_result(result):
  """結果を表示します"""

  # ステータスコードは'status_code'キーに格納
  status_code = result.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(result, indent=2))
    return

  # 結果表示
  print("status_code: {0}".format(result.get('status_code', "")))
  print(result.get('data', ""))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Disconnect interface to a specified network connector endpoint.')
    parser.add_argument('--ncep-id', dest='ncep_id', metavar="id", required=True, help='The network connector endpoint id.')
    parser.add_argument('--port-id', dest='port_id', metavar="id", required=True, help='The port id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    ncep_id = args.ncep_id
    port_id = args.port_id
    dump = args.dump

    # 対象のコネクタエンドポイントID
    # ncep_id = "ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"

    # 切断するポートID
    # port_id = "863f2404-4a92-4991-8fab-e4312682dd86"

    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(port_id=port_id)

    # 実行
    result = access_api(ncep_id=ncep_id, data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
