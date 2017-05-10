#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/routers/{router_id}
Delete router
論理ルータを削除する
外部ゲートウェイインターフェイスがある場合はそれを削除する
"""

"""
実行例（成功した場合は特にデータは戻りません）

bash-4.4$ ./k5-delete-router.py ad3ddc47-6303-48e8-87ad-cb0333c93112
status_code: 204

実行例（失敗した場合はエラーメッセージが戻ります）

bash-4.4$ ./k5-delete-router.py ad3ddc47-6303-48e8-87ad-cb0333c93112
{
  "Content-Type": "application/json",
  "data": {
    "NeutronError": "Router ad3ddc47-6303-48e8-87ad-cb0333c93112 could not be found",
    "request_id": "a1370cc6-b26f-477f-a7c9-a1f6885141f7"
  },
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
def main(router_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/routers/" + router_id

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
    print("Usage: {0} {1}".format(sys.argv[0], "router_id"))
    exit(1)

  main(router_id=sys.argv[1])
