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
# APIにアクセスする
#
def access_api(network_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/networks/" + network_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

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
    parser = argparse.ArgumentParser(description='Deletes a specified network and its associated resources.')
    parser.add_argument('network_id', metavar='id', help='The network id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    network_id = args.network_id
    dump = args.dump

    # 実行
    result = access_api(network_id=network_id)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
