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
if not here("../lib") in sys.path:
  sys.path.append(here("../lib"))

if not here("../lib/site-packages") in sys.path:
  sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  exit(1)


#
# APIにアクセスする
#
def access_api(subnet_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/subnets/" + subnet_id

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
    parser = argparse.ArgumentParser(description='Deletes a specified subnet.')
    parser.add_argument('subnet_id', metavar='id', help='The subnet id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    subnet_id = args.subnet_id
    dump = args.dump

    # 実行
    result = access_api(subnet_id=subnet_id)

    # 得たデータを処理する
    print_result(result, dump=dump)


  # 実行
  main()
