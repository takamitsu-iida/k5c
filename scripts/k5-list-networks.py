#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/networks
List networks
テナントがアクセスするネットワークの一覧を表示する
"""

"""
実行例

bash-4.4$ ./k5-list-networks.py
GET /v2.0/networks
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
375c49fa-a706-4676-b55b-2d3554e5db6a  inf_az2_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
4516097a-84dd-476f-824a-6b2fd3cc6499  inf_az2_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
852e40a7-82a3-4196-8b84-46f55d01ccba  inf_az2_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
abe76a93-87c3-4635-b0f3-40f794165c26  inf_az2_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
bfca06b3-0b23-433f-96af-4f54bf963e5f  inf_az2_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========
bash-4.4$
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
  url = k5config.URL_NETWORKS

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

  # ネットワーク一覧はデータオブジェクトの中の'networks'キーに配列として入っている
  networks_list = []
  for item in data.get('networks', []):
    networks_list.append([item.get('id', ''), item.get('name', ''), item.get('tenant_id', ''), item.get('availability_zone', ''), item.get('status', '')])

  # 一覧を表示
  print("GET /v2.0/networks")
  print(tabulate(networks_list, headers=['id', 'name', 'tenant_id', 'az', 'status'], tablefmt='rst'))

  # 結果を返す
  return r


if __name__ == '__main__':
  main(dump=False)
