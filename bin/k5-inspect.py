#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
各種情報を採取してtinydbに格納します。
あとは煮るなり焼くなり、なんとでも。
"""

if __name__ == '__main__':

  import argparse
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
  except ImportError:
    logging.error("k5cモジュールのインポートに失敗しました")
    sys.exit(1)

  # k5cクライアント
  c = k5c.Client()

  # アプリケーションのホームディレクトリ
  app_home = here("..")

  # データベースの名前
  # $app_home/data/db.json
  database_file = os.path.join(app_home, "data", "db.json")

  # 情報の保管庫として辞書型を保存できるtinydbを使う
  try:
    from tinydb import Query
    from tinydb import TinyDB
  except ImportError as e:
    logging.error("tinydb not found. pip install tinydb")
    sys.exit(1)

  # tinydbの使い方
  #
  # 辞書型を格納する
  # db.insert({'name': 'John', 'age': 22})
  #
  # 全データを配列で取得する
  # db.all()
  #
  # 検索する
  # q = Query()
  # db.search(q.name == 'John')
  #
  # アップデートする
  # nameがJohnになっている辞書型の'age'フィールドを23に変更する
  # db.update({'age': 23}, q.name == 'John')
  #
  # 削除する
  # db.remove(q.age < 22)
  #
  # 全部削除する
  # db.purge()

  # 情報を保管するデータベース
  db = TinyDB(database_file)

  # 検索用のクエリオブジェクト
  q = Query()


  def get(url=""):
    """c.get()のラッパー"""
    print(url, end="", flush=True)
    r = c.get(url=url)
    print("   ...done", flush=True)

    # ステータスコードは'status_code'キーに格納
    status_code = r.get('status_code', -1)
    if status_code < 200 or status_code >= 300:
      return None

    # データは'data'キーに格納
    data = r.get('data', None)
    if not data:
      return None

    # dbに格納
    db.insert(data)

    return data


  def create_cache():
    """k5-list-xxxとk5-show-xxxの実行結果のキャッシュを作成します。"""

    #
    # List Network Connector Pools
    #
    #"data": {
    #  "network_connector_pools": [
    url = k5c.EP_NETWORK + "/v2.0/network_connector_pools"
    data = get(url=url)

    #
    # List Network Connectors
    #
    #"data": {
    #  "network_connectors": [
    url = k5c.EP_NETWORK + "/v2.0/network_connectors"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('network_connectors', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show Network Connector
        #
        #"data": {
        #  "network_connector": {
        url = k5c.EP_NETWORK + "/v2.0/network_connectors/" + item_id
        get(url=url)

    #
    # List Network Connector Endpoints
    #
    #  "data": {
    #    "network_connector_endpoints": [
    url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('network_connector_endpoints', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show Network Connector Endpoint
        #
        #"data": {
        #  "network_connector_endpoint": {
        url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints/" + item_id
        get(url=url)

        #
        # List Connected Interfaces of Network Connector Endpoint
        #
        #"data": {
        #  "network_connector_endpoint": {
        #    "interfaces": [
        url = k5c.EP_NETWORK + "/v2.0/network_connector_endpoints/" + item_id + "/interfaces"
        get(url=url)

    #
    # List networks
    #
    url = k5c.EP_NETWORK + "/v2.0/networks"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('networks', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show network
        #
        #  "data": {
        #    "network": {
        url = k5c.EP_NETWORK + "/v2.0/networks/" + item_id
        get(url=url)

    #
    # List subnets
    #
    # "data": {
    #   "subnets": [
    url = k5c.EP_NETWORK + "/v2.0/subnets"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('subnets', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show subnet
        #
        #"data": {
        #  "subnet": {
        url = k5c.EP_NETWORK + "/v2.0/subnets/" + item_id
        get(url=url)

    #
    # List ports
    #
    #"data": {
    #  "ports": [
    url = k5c.EP_NETWORK + "/v2.0/ports"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('ports', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show port
        #
        #"data": {
        #  "port": {
        url = k5c.EP_NETWORK + "/v2.0/ports/" + item_id
        get(url=url)

    #
    # List routers
    #
    #"data": {
    #  "routers": [
    url = k5c.EP_NETWORK + "/v2.0/routers"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('routers', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show router
        #
        #"data": {
        #  "router": {
        url = k5c.EP_NETWORK + "/v2.0/routers/" + item_id
        get(url=url)

    #
    # List floating IPs
    #
    #  "data": {
    #    "floatingips": [
    url = k5c.EP_NETWORK + "/v2.0/floatingips"
    data = get(url=url)
    if not data:
      logging.error("GET failed.")
      return 1

    item_list = data.get('floatingips', [])
    for item in item_list:
      item_id = item.get('id', None)
      if item_id:
        #
        # Show floating IP details
        #
        #  "data": {
        #    "floatingip": {
        url = k5c.EP_NETWORK + "/v2.0/floatingips/" + item_id
        get(url=url)

    return 0


  def main():
    """メイン"""

    parser = argparse.ArgumentParser(description='Inspect K5 network.')
    parser.add_argument('-c', '--create', action='store_true', default=False, help='Create cache')
    args = parser.parse_args()
    create = args.create

    if create:
      return create_cache()

    #o = db.search(q.network_connector_endpoint.interfaces != None)
    #print(o)

    #o = db.search(q.subnet.cidr == '10.1.1.0/24')
    #print(o)

    o = db.search(q.subnet.name.search('iida'))
    print(o)




    return 0


  # 実行
  sys.exit(main())
