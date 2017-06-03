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
  if getattr(sys, 'frozen', False):
    # cx_Freezeで固めた場合は実行ファイルからの相対パス
    return os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
  else:
    # 通常はこのファイルの場所からの相対パス
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
# APIにアクセスする
#
def access_api(router_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/routers/" + router_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

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
    parser = argparse.ArgumentParser(description='Deletes a logical router and, if present, its external gateway interface.')
    parser.add_argument('router_id', metavar='id', help='The router id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    router_id = args.router_id
    dump = args.dump

    if router_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          # print(uuid)
          # 実行
          result = access_api(router_id=uuid)
          # 得たデータを処理する
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(router_id=router_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
