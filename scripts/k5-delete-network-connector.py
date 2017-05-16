#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/network_connectors/{network connector id}　★
Deletes Network Connector
ネットワークコネクタを削除する

注意：
　・削除するネットワークコネクタのidは実行時の引数として指定
　・k5-list-network-connectors.pyで調べる

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

"""
実行例（成功時）
bash-4.4$ ./k5-delete-network-connector.py d6901be5-bbab-4194-ae21-1eb78822aacb
status_code: 204

実行例（失敗時）
bash-4.4$ ./k5-delete-network-connector.py d6901be5-bbab-4194-ae21-1eb78822aacb
status_code: 404
{'NeutronError': {'detail': '', 'message': 'Network d6901be5-bbab-4194-ae21-1eb78822aacb could not be found', 'type': 'NetworkNotFound'}}
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
# メイン
#
def main(network_connector_id=''):
  """メイン関数"""
  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/network_connectors/" + network_connector_id

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
    parser = argparse.ArgumentParser(description='Deletes a specified network connector.')
    parser.add_argument('network_connector_id', help='The network connector id.')
    args = parser.parse_args()
    network_connector_id = args.network_connector_id
    main(network_connector_id=network_connector_id)

  # 実行
  run_main()
