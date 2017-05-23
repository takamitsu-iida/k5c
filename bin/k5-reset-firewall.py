#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/fw/firewalls/{firewall-id}/reset_connections
Update firewall(Connection reset)
ファイアーウォールが管理するコネクションをすべて削除する

APIマニュアルから引用

API応答してから数秒後、Firewallが適用されたルータの管理するコネクションをすべて削除します。
これによりFirewallに対して設定したルールが通信に反映されます。
なお、Firewallが適用されたルータを経由して通信中だった既存の通信は、
Firewallで許可されている通信を含め一度すべて切断されます。
なお、通信許可のルールが存在する場合は、切断は一時的なものであり、通信は継続されます。
"""

"""
実行例（成功した場合は特にデータは戻りません）

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


#
# リクエストデータを作成
#
def make_request_data():
  """リクエストデータを作成して返却します"""

  target_object = {
    'target': None
  }

  return target_object


#
# APIにアクセスする
#
def access_api(firewall_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/fw/firewalls/" + firewall_id + "/reset_connections"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッドで更新して、結果のオブジェクトを得る
  r = c.put(url=url, data=data)

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
  # データ部は誤解を生むので表示しない {'target': None}
  # print(result.get('data', ""))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Connection reset for applying firewall rule to the current communication immediately.')
    parser.add_argument('firewall_id', metavar='id', help='The firewall id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    firewall_id = args.firewall_id
    dump = args.dump

    if firewall_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          # 実行
          data = make_request_data()
          result = access_api(firewall_id=uuid, data=data)
          # 表示
          print("firewall_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    data = make_request_data()
    result = access_api(firewall_id=firewall_id, data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
