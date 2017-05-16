#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/routers
List routers
テナント内でアクセス可能なルータのリストを表示する。
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
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(dump=False):
  """メイン関数"""
  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/routers"

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

  # ルータ一覧はデータオブジェクトの中の'routers'キーに配列として入っている
  #"data": {
  #  "routers": [
  #    {
  #      "routes": [],
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "status": "ACTIVE",
  #      "name": "iida-test-router-1",
  #      "id": "5359cce0-cd5c-48e8-891a-659c5ae62f65",
  #      "external_gateway_info": null,
  #      "availability_zone": "jp-east-1a",
  #      "admin_state_up": true
  #    },
  routers_list = []
  for item in data.get('routers', []):
    routers_list.append([item.get('id', ''), item.get('name', ''), item.get('tenant_id', ''), item.get('availability_zone', ''), item.get('status', '')])

  # 一覧を表示
  print("GET /v2.0/routers")
  print(tabulate(routers_list, headers=['id', 'name', 'tenant_id', 'az', 'status'], tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main():
    """メイン関数を実行します"""
    import argparse
    parser = argparse.ArgumentParser(description='List routers')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    dump = args.dump
    main(dump=dump)

  # 実行
  run_main()
