#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/subnets/{subnet_id}
Delete subnet
指定したサブネットを削除する

注意：
　・削除するサブネットのidは実行時の引数として指定
　・サブネットを削除するとDHCPも停止するので、DHCP利用時はネットワークごと削除して作り直すこと
"""

"""
実行例（成功した場合は特にデータは戻りません）
bash-4.4$ ./k5-delete-subnet.py 97c0a17a-d062-4869-abde-32e8d426b6ca
status_code: 204

実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-subnet.py 97c0a17a-d062-4869-abde-32e8d426b6ca
{
  "data": {
    "NeutronError": {
      "message": "Subnet 97c0a17a-d062-4869-abde-32e8d426b6ca could not be found",
      "type": "SubnetNotFound",
      "detail": ""
    }
  },
  "Content-Type": "application/json;charset=UTF-8",
  "status_code": 404
}
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

try:
  from k5c import k5config  # need info in k5config.py
except ImportError as e:
  logging.exception("k5configモジュールの読み込みに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(subnet_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/subnets/" + subnet_id

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
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "subnet_id"))
    exit(1)

  main(subnet_id=sys.argv[1])
