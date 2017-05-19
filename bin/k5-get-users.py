#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ユーザの取得
・全体管理者の権限が必要
"""

"""
実行例

k5-get-users.py
======  ================================  ========  ================================
name    id                                locale    domain_id
======  ================================  ========  ================================
admin   f48b476f23d84952ae981d264e895aad  ja        e6eb13c4e52b4a60ac17aa925d1aa14c
tiida   0b507503256542afa30ff75b4d65962f  ja        e6eb13c4e52b4a60ac17aa925d1aa14c
======  ================================  ========  ================================
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
  sys.exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)


#
# APIにアクセスする
#
def access_api():
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_IDENTITY + "/v3/users?domain_id=" + k5c.DOMAIN_ID

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # ユーザ一覧はデータオブジェクトの中の'users'キーに配列として入っている
  #"data": {
  #  "links": {
  #    "next": null,
  #    "previous": null,
  #    "self": "http://identity.jp-east-1.cloud.global.fujitsu.com/v3/users"
  #  },
  #  "users": [
  #    {
  #      "id": "f48b476f23d84952ae981d264e895aad",
  #      "links": {
  #        "self": "http://identity.jp-east-1.cloud.global.fujitsu.com/v3/users/f48b476f23d84952ae981d264e895aad"
  #      },
  #      "default_project_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "domain_id": "e6eb13c4e52b4a60ac17aa925d1aa14c",
  #      "enabled": true,
  #      "locale": "ja",
  #      "name": "admin"
  #    },
  users_list = []
  for item in data.get('users', []):
    users_list.append([item.get('name', ''), item.get('id', ''), item.get('locale', ''), item.get('domain_id', '')])

  # ユーザ一覧を表示
  print(tabulate(users_list, headers=['name', 'id', 'locale', 'domain_id'], tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Get users.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 得たデータを処理する
    print_result(result, dump=dump)

    return 0

  # 実行
  sys.exit(main())
