#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/network_connector_endpoints{network connector endpoint id}/connect
Connect Network Connector Endpoint
ネットワークコネクタエンドポイントにインターフェイスを接続する
"""

"""
実行例(成功)

bash-4.4$ ./bin/k5-connect-network-connector-endpoint.py \
--ncep-id 31b72eba-f471-408d-a9da-3bb317b01b1b \
--port-id f75bf3a5-0ac0-47d8-a933-34026d852ec1

status_code: 200
{'interface': {'port_id': 'f75bf3a5-0ac0-47d8-a933-34026d852ec1'}}
bash-4.4$
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


#
# リクエストデータを作成する
#
def make_request_data(port_id=""):
  """リクエストデータを作成して返却します"""

  # 接続対象となるインタフェースのオブジェクト
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
  url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id + "/connect"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドを発行して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

  return r


#
# 結果を表示する
#
def print_result(result, dump=False):
  """結果を表示します"""

  # 中身を確認
  if dump:
    print(json.dumps(result, indent=2))
    return

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
    parser = argparse.ArgumentParser(description='Connects interface to a specified network connector endpoint.')
    parser.add_argument('--ncep-id', dest='ncep_id', metavar='id', required=True, help='The network connector endpoint id.')
    parser.add_argument('--port-id', dest='port_id', metavar='id', required=True, help='The port id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    ncep_id = args.ncep_id
    port_id = args.port_id
    dump = args.dump

    # 対象のコネクタエンドポイントID
    # ncep_id = "ed44d452-cbc4-4f4c-9c87-03fdf4a7c965"
    #
    # 接続するポートID
    # port_id = "305485fb-3bff-4230-a1f6-f594ec4ea1fb"
    #
    # jsonをダンプ
    # dump = False

    # リクエストデータを作成
    data = make_request_data(port_id=port_id)

    # 実行
    result = access_api(ncep_id=ncep_id, data=data)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
