#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
トークンを取得してダンプします。
"""

"""
実行例

bash-4.4$ ./k5-token.py
{
  "expires_at": "2017-05-02T13:31:28.092961Z",
  "X-Subject-Token": "f240eccd302f4a31b3ccdb4b0d1bcd7f",
  "issued_at": "2017-05-02T10:31:28.092987Z"
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
sys.path.append(here("../lib"))
sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  exit(1)


def main():
  """メイン関数"""
  # Clientクラスをインスタンス化
  c = k5c.Client()

  # トークンを取得
  token = c.getToken()

  # tokenオブジェクトをダンプ表示
  print(json.dumps(token, indent=2))


if __name__ == '__main__':
  main()
