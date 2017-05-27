#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
k5-inspect.py --create
各種情報を採取してtinydbに格納します。
追記していくので、事前にdb.jsonは削除してください。
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
    # "data": {
    #   "networks": [
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


  def search_port_by_device_id(device_id):
    """device_idが一致するポートの一覧を配列で返します"""

    # 戻り値
    port_list = []

    results = db.search(q['port'].device_id == device_id)
    if results:
      for item in results:
        port_list.append(item.get('port'))

    return port_list


  def search_port_by_network_id(network_id):
    """network_idが一致するポートの一覧を配列で返します"""

    # 戻り値
    port_list = []

    results = db.search(q['port'].network_id == network_id)
    if results:
      for item in results:
        port_list.append(item.get('port'))

    return port_list


  def get_port_by_fixed_ip(ip_address):
    """ip_addressが一致するポートを返します"""

    #  "port": {
    #    "fixed_ips": [
    #      {
    #        "ip_address": "192.168.0.2",
    #        "subnet_id": "8ed6dd7b-2ae3-4f68-81c9-e5d9e074b67a"
    #      }
    #    ],
    # この構造からip_addressが一致するものを見つける
    # 単純なオペレータで表現するのは難しいので無名関数を使う

    # fixed_ips配列の要素がなからず1個と決めつけるならこれでいいけど・・・
    # func = lambda x: x[0].get('ip_address', '') == ip_address

    # ラムダ式とリスト内包を組み合わせて一致する要素があるかを確認する
    func = lambda x: ip_address in [y.get('ip_address', '') for y in x]

    # testにこの関数を渡して評価する
    port = db.get(q['port'].fixed_ips.test(func))
    if port:
      return port.get('port')
    return None


  def inspect_router(router):
    """ルータの中身を確認します"""
    r_id = router.get('id')
    name = router.get('name')
    print(name)

    # このルータを親にしているポートを探す
    port_list = search_port_by_device_id(r_id)
    if port_list:
      for item in port_list:
        print(' '*2 + "port-id: ", end='')
        print(item.get('id'))
    else:
      print(' '*2, end='')
      print("This router has no port.")

    print("")


  def inspect_network(network):
    """ネットワークの中身を確認します"""
    n_id = network.get('id')
    name = network.get('name')
    print(name)

    # このIDを親にしているポートを探す
    ports = search_port_by_network_id(n_id)
    if ports:
      print(' '*2, end='')
      print(str(len(ports)))
    else:
      print(' '*2, end='')
      print("This port does not have port.")
    print("")


  def get_list(key):
    """k5-list-xxxの結果の配列をdbから取り出して返します"""
    value = db.get(q[key].exists())
    return value.get(key, [])


  def main():
    """メイン"""

    parser = argparse.ArgumentParser(description='Inspect K5 network.')
    parser.add_argument('-c', '--create', action='store_true', default=False, help='Create cache')
    args = parser.parse_args()
    create = args.create

    if create:
      return create_cache()

    #
    # 使えるアトリビュート
    #

    # network_connector_pools
    # network_connectors
    # network_connector
    # network_connector_endpoints
    # network_connector_endpoint
    # network_connector_endpoint
    # networks
    # network
    # subnets
    # subnet
    # ports
    # port
    # routers
    # router
    # floatingips
    # floatingip

    # 簡単なテスト
    #
    # o = db.search(q.subnet.cidr == '10.1.1.0/24')
    # print(o)
    #
    # o = db.search(q.subnet.name.search('iida'))
    # print(o)
    #
    # print(get_port_by_fixed_ip('10.0.1.1'))


    # ルータ一覧の配列を取り出す
    routers = get_list('routers')
    for item in routers:
      inspect_router(item)

    # ネットワーク一覧の配列を取り出す
    #networks = get_list('networks')
    #for item in networks:
    #  inspect_network(item)

    return 0


  # 実行
  sys.exit(main())
