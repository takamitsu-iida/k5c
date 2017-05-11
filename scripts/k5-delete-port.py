#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/ports/{port_id}
Delete port
指定したポートを削除する

注意：
　・削除するポートのidは実行時の引数として指定
"""

"""
実行例（成功した場合は特にデータは戻りません）
bash-4.4$ ./k5-delete-port.py 9c3e757b-298a-498c-8770-31e457d44ac0
status_code: 204

実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-port.py 9c3e757b-298a-498c-8770-31e457d44ac0
{
  "status_code": 404,
  "data": {
    "NeutronError": {
      "detail": "",
      "message": "Port 9c3e757b-298a-498c-8770-31e457d44ac0 could not be found",
      "type": "PortNotFound"
    }
  },
  "Content-Type": "application/json;charset=UTF-8"
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
def main(port_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/ports/" + port_id

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
    parser = argparse.ArgumentParser(description='Deletes a specified port.')
    parser.add_argument('port_id, help="Port id')
    args = parser.parse_args()
    port_id = args.port_id
    main(port_id=port_id)

  # 実行
  run_main()
