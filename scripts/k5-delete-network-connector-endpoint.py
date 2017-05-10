#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/network_connector_endpoints/{network connector endpoint id}
Deletes Network Connector Endpoint
ネットワークコネクタエンドポイントを削除する

注意：
　・削除するネットワークコネクタエンドポイントのidは実行時の引数として指定
　・k5-list-network-connector-endpoints.pyで調べる

bash-4.4$ ./k5-list-network-connector-endpoints.py
GET /v2.0/network_connector_endpoints
====================================  =======================================  ====================================
id                                    name                                     network_connector_id
====================================  =======================================  ====================================
f9dec519-8517-4562-91c3-1c09e5eb4c19  iida-test-network-connecotor-endpoint-1  eceb05fd-8aee-470b-bdca-95f789f181c1
====================================  =======================================  ====================================
bash-4.4$
"""

"""
実行例（成功時）
bash-4.4$ ./k5-delete-network-connector-endpoint.py f9dec519-8517-4562-91c3-1c09e5eb4c19
status_code: 204

実行例（失敗時）
bash-4.4$ ./k5-delete-network-connector-endpoint.py f9dec519-8517-4562-91c3-1c09e5eb4c19
{
  "data": {
    "NeutronError": {
      "detail": "",
      "type": "NetworkConnectorEndpointNotFound",
      "message": "network connector endpoint f9dec519-8517-4562-91c3-1c09e5eb4c19 not found."
    },
    "request_id": "fd7bd641-13e3-4354-ba7c-c4206be1e6c9"
  },
  "Content-Type": "application/json;charset=utf-8",
  "status_code": 404
}
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
def main(ncep_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/network_connector_endpoints/" + ncep_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

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

  def run_main():
    """メイン関数を実行します"""
    import argparse
    parser = argparse.ArgumentParser(description='Delete network connector endpoint.')
    parser.add_argument('ncep_id, help="Network connector endpoint id')
    args = parser.parse_args()
    ncep_id = args.ncep_id
    main(ncep_id=ncep_id)

  # 実行
  run_main()
