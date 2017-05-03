#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/networks/{network_id}
Delete network
指定したネットワークとそれに関連付けられたリソースを削除する

注意：
　・削除するネットワークのidは実行時の引数として指定
"""

"""
実行例（成功した場合は特にデータは戻りません）
bash-4.4$ ./k5-delete-network.py 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b
status_code: 204

実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-network.py 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b
status_code: 404
{'NeutronError': {'type': 'NetworkNotFound', 'detail': '', 'message': 'Network 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b could not be found'}}
bash-4.4$
"""

import logging
import os
import sys

# 通常はWARN
# 多めに情報を見たい場合はINFO
logging.basicConfig(level=logging.WARN)

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.error("k5cモジュールのインポートに失敗しました")
  logging.error(e)
  exit(1)

try:
  from k5c import k5config  # need info in k5config.py
except ImportError:
  logging.error("k5configモジュールの読み込みに失敗しました。")
  exit(1)


#
# メイン
#
def main(network_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.URL_NETWORK + "/" + network_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

  # 戻り値は'status_code'キーに格納
  # ステータスコードが負の場合は、何かおかしかったということ
  if r.get('status_code', -1) < 0:
    logging.error("failed to DELETE %s", url)
    exit(1)

  # 結果表示
  print("status_code: {0}".format(r.get('status_code', "")))
  print(r.get('data', ""))


if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: {0} {1}".format(sys.argv[0], "network_id"))
    exit(1)

  main(network_id=sys.argv[1])
