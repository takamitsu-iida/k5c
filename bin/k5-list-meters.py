#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2/meters
監視項目一覧取得
指定されたクエリに基づいて、すべての監視項目を取得します。
"""

"""
実行例

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
  url = k5c.EP_CEILOMETER + "/v2/meters"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

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

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # メータ一覧はデータオブジェクトの中に配列として入っている
  #bash-4.4$ ./k5-list-meters.py --dump
  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "data": [
  #    {
  #      "user_id": "0b507503256542afa30ff75b4d65962f",
  #      "resource_id": "c8f88a25-7665-483f-8d33-a6a311801ac6",
  #      "source": "fcx",
  #      "meter_id": "YzhmODhhMjUtNzY2NS00ODNmLThkMzMtYTZhMzExODAxYWM2K2ZjeC5pcC5mbG9hdGluZw==\n",
  #      "name": "fcx.ip.floating",
  #      "project_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "unit": "ip",
  #      "type": "gauge"
  #    },

  disp_keys = ['name', 'unit', 'type', 'source']  #, 'project_id', 'user_id']

  disp_list = []
  for item in result.get('data', []):
    row = []
    for key in disp_keys:
      row.append(item.get(key, ''))
    disp_list.append(row)

  # sorted()を使ってnameをもとにソートする
  # nameは配列の1番めの要素なのでインデックスは0
  disp_list = sorted(disp_list, key=lambda x: x[0])

  # 一覧を表示
  print(tabulate(disp_list, headers=disp_keys, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='List meters')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump

    # 実行
    result = access_api()

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
