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

try:
  from tabulate import tabulate
except ImportError as e:
  logging.error("tabulateモジュールのインポートに失敗しました")
  exit(1)

#
# メイン
#
def main(dump=False):
  """メイン関数"""
  # 接続先
  url = k5config.URL_USERS

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  # 中身を確認
  if dump:
    print(json.dumps(r, indent=2))
    return r

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    return r

  # データは'data'キーに格納
  data = r.get('data', None)
  if not data:
    logging.error("no data found")
    return r

  # ユーザ一覧はデータオブジェクトの中の'users'キーに配列として入っている
  users_list = []
  for item in data.get('users', []):
    users_list.append([item.get('name', ''), item.get('id', ''), item.get('locale', ''), item.get('domain_id', '')])

  # ユーザ一覧を表示
  print(tabulate(users_list, headers=['name', 'id', 'locale', 'domain_id'], tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  main(dump=False)
