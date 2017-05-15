#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/fw/firewall_rules/{firewall_rule_id}
Delete firewall rule
ファイアーウォールのルールを削除する
"""

"""
実行例（成功した場合は特にデータは戻りません）

bash-4.4$ ./k5-delete-fw-rule.py 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c
status_code: 204

bash-4.4$
実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-fw-rule.py 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c
{
  "status_code": 404,
  "Content-Type": "application/json;charset=UTF-8",
  "data": {
    "NeutronError": {
      "detail": "",
      "type": "FirewallRuleNotFound",
      "message": "Firewall Rule 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c could not be found."
    }
  }
}
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
  from k5c import k5config  # need info in k5config.py
except ImportError as e:
  logging.exception("k5configモジュールの読み込みに失敗しました: %s", e)
  exit(1)

#
# メイン
#
def main(firewall_rule_id=''):
  """メイン関数"""
  # 接続先
  url = k5config.EP_NETWORK + "/v2.0/fw/firewall_rules/" + firewall_rule_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

  # ステータスコードは'status_code'キーに格納
  status_code = r.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(r, indent=2))
    return r

  # 結果表示
  print("status_code: {0}".format(r.get('status_code', "")))
  print(r.get('data', ""))

  # 結果を返す
  return r


if __name__ == '__main__':

  def run_main():
    """メイン関数を実行します"""
    import argparse
    parser = argparse.ArgumentParser(description='Deletes a firewall rule.')
    parser.add_argument('firewall_rule_id', help='The firewall rule id.')
    args = parser.parse_args()
    firewall_rule_id = args.firewall_rule_id
    main(firewall_rule_id=firewall_rule_id)

  # 実行
  run_main()
