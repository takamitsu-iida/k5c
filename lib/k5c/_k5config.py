#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
設定情報
"""

#
# K5ポータル
# https://s-portal.cloud.global.fujitsu.com/SK5PCOM001/
#

# 契約番号
DOMAIN_NAME = ""  # ここを書き換え

# ドメインID(32桁)
# IaaSポータルから[管理]→[利用者管理]→[グループ]
DOMAIN_ID = ""  # ここを書き換え

# プロジェクトID(32桁)
PROJECT_ID = ""  # ここを書き換え

# ユーザ情報
USERNAME = ""  # ここを書き換え
PASSWORD = ""  # ここを書き換え

# 対象リージョン
REGION = "jp-east-1"  # ここを書き換え

#
# エンドポイント
#
EP_TOKEN = "https://identity." + REGION + ".cloud.global.fujitsu.com"
EP_IDENTITY = "https://identity." + REGION + ".cloud.global.fujitsu.com"
EP_NETWORK = "https://networking." + REGION + ".cloud.global.fujitsu.com"

#
# プロキシ設定
#
USE_PROXY = False
# USE_PROXY = True

PROXIES = {
  'http': "http://username:password@proxyserver:8080",  # ここを書き換え
  'https': "http://username:password@proxyserver:8080"  # ここを書き換え
}

if not USE_PROXY:
  PROXIES = None

#
# 動作設定
#
TIMEOUT = 15
