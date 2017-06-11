#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ネットワークコネクタエンドポイント周辺はまだ未実装。

k5-inspect.py --create
　各種情報を採取してtinydbに格納します。
　追記していくので、事前にconf/db.jsonをリネームするか削除してください。

  採取対象
    List Network Connector Pools
    List Network Connectors
    Show Network Connector

    List Network Connector Endpoints
    Show Network Connector Endpoint
    List Connected Interfaces of Network Connector Endpoint

    List networks
    Show network

    List subnets
    Show subnet

    List ports
    Show port

    List routers
    Show router

    List floating IPs
    Show floating IP details
"""

if __name__ == '__main__':

  import argparse
  import codecs
  import json
  import logging
  import os
  import sys

  def here(path=''):
    """相対パスを絶対パスに変換して返却します"""
    if getattr(sys, 'frozen', False):
      # cx_Freezeで固めた場合は実行ファイルからの相対パス
      return os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
    else:
      # 通常はこのファイルの場所からの相対パス
      return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

  # libフォルダにおいたpythonスクリプトを読みこませるための処理
  if not here("../lib") in sys.path:
    sys.path.append(here("../lib"))

  if not here("../lib/site-packages") in sys.path:
    sys.path.append(here("../lib/site-packages"))

  # アプリケーションのホームディレクトリ
  app_home = here("..")

  # デフォルトのデータベースのファイル名
  # $app_home/data/db.json
  database_file = os.path.join(app_home, "data", "db.json")

  # 引数処理
  parser = argparse.ArgumentParser(description='Inspect K5 network.')
  parser.add_argument('-c', '--create', action='store_true', default=False, help='Create cache')
  parser.add_argument('-r', '--router', action='store_true', default=False, help='Inspect by router')
  parser.add_argument('-nc', '--network-connector', action='store_true', default=False, help='Inspect by network connector')
  parser.add_argument('-n', '--network', action='store_true', default=False, help='Inspect by network')
  parser.add_argument('-f', '--filename', dest='filename', metavar='file', default=database_file, help='The database file. default: '+database_file)
  parser.add_argument('-g', '--generate', action='store_true', default=False, help='Generate data')
  parser.add_argument('-d', '--dump', action='store_true', default=False, help='Dump all json')
  args = parser.parse_args()

  # 情報の保管庫として辞書型を保存できるtinydbを使う
  try:
    from tinydb import Query
    from tinydb import TinyDB
  except ImportError as e:
    logging.error("tinydb not found. pip install tinydb")
    sys.exit(1)

  # キャッシュを新規作成する場合には、古いファイルを削除する
  if args.create:
    if os.path.isfile(args.filename):
      try:
        os.remove(args.filename)
      except OSError:
        pass

  # 情報を保管するデータベース
  db = TinyDB(args.filename)

  # 検索用のクエリオブジェクト
  q = Query()

  #
  # このデータベースで使えるアトリビュート
  #

  # network_connector_pools
  # network_connectors
  # network_connector
  # network_connector_endpoints
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


  def create_cache():
    """k5-list-xxxとk5-show-xxxを実行して結果をキャッシュします。"""

    try:
      from k5c import k5c
    except ImportError:
      logging.error("k5cモジュールのインポートに失敗しました")
      sys.exit(1)

    # k5cクライアント
    c = k5c.Client()

    # これだけのためにデコレータを定義するのはさすがに面倒なので
    # c.get()にラッパー関数をかぶせます
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
        # ここだけは特別な処理が必要
        # get(url=url)
        print(url, end="", flush=True)
        r = c.get(url=url)
        print("   ...done", flush=True)

        # ステータスコードは'status_code'キーに格納
        status_code = r.get('status_code', -1)
        if status_code < 200 or status_code >= 300:
          continue

        # データは'data'キーに格納
        data = r.get('data', None)
        if not data:
          continue

        # dbに格納
        db.update(data, q['network_connector_endpoint'].id == item_id)

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


  def search_router_with_external_gateway_info():
    """external_gateway_infoを持っているルータを配列で返します"""

    # 戻り値
    router_list = []
    results = db.search(q['router'].external_gateway_info.exists())
    if results:
      for item in results:
        router_list.append(item.get('router'))

    return router_list

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


  def get_port_by_id(port_id):
    """指定されたIDのポートを返却します"""
    port = db.get(q['port'].id == port_id)
    if port:
      return port.get('port')
    return None


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


  def get_network_connector_pool_by_id(network_connector_pool_id):
    """指定されたIDのネットワークコネクタプールを返却します"""
    ncp_list = get_list('network_connector_pools')
    for ncp in ncp_list:
      ncp_id = ncp.get('id')
      if ncp_id == network_connector_pool_id:
        return ncp
    return None


  def get_network_connector_by_id(network_connector_id):
    """指定されたIDのネットワークコネクタを返却します"""
    nc = db.get(q['network_connector'].id == network_connector_id)
    if nc:
      return nc.get('network_connector')
    return None


  def get_network_connector_endpoint_by_id(ncep_id):
    """指定されたIDのコネクタエンドポイントを返却します"""
    ncep = db.get(q['network_connector_endpoint'].id == ncep_id)
    if ncep:
      return ncep.get('network_connector_endpoint')
    return None

  def get_network_by_id(network_id):
    """指定されたIDのネットワークを返却します"""
    network = db.get(q['network'].id == network_id)
    if network:
      return network.get('network')
    return None


  def get_subnet_by_id(subnet_id):
    """指定されたIDのサブネットを返却します"""
    subnet = db.get(q['subnet'].id == subnet_id)
    if subnet:
      return subnet.get('subnet')
    return None


  def inspect_router(router):
    """ルータの中身を確認します"""

    name = router.get('name')
    if not name:
      name = 'NO-NAME'
    print("Router {} is {}, Admin state is {}".format(name, router.get('status'), router.get('admin_state_up')))
    print("{}UUID is {}".format(' '*2, router.get('id')))
    print("{}Tenant uuid is {}".format(' '*2, router.get('tenant_id')))
    print("{}Availability zone is {}".format(' '*2, router.get('availability_zone')))
    eg_info = router.get('external_gateway_info', None)
    if eg_info:
      print("{}External gateway network is {} ,snat is {}".format(' '*2, eg_info.get('network_id'), eg_info.get('enable_snat')))
    else:
      print("{}External gateway is not set.")
    print("{}Routing table".format(' '*2))
    if router.get('routes'):
      for route in router.get('routes', []):
        print("{}{} via {}".format(' '*4, route.get('destination'), route.get('nexthop')))
    else:
      print("{}No route is set.".format(' '*4))

    # このルータを親にしているポートを探す
    port_list = search_port_by_device_id(router.get('id'))
    if port_list:
      for port in port_list:
        name = port.get('name')
        if not name:
          name = 'NO-NAME'
        print("{}Port {} is {}, Admin state is {}".format(' '*2, name, port.get('status'), port.get('admin_state_up')))
        print("{}Port uuid is {}".format(' '*4, port.get('id', '')))
        print("{}Port is attached to the Network {}".format(' '*4, port.get('network_id', '')))
        print("{}binding:vnic_type is {}".format(' '*4, port.get('binding:vnic_type')))
        print("{}Hardware address is {}".format(' '*4, port.get('mac_address')))
        for fixedip in port.get('fixed_ips', []):
          print("{}Internet address is {} , Subnet is {}".format(' '*4, fixedip.get('ip_address'), fixedip.get('subnet_id')))
    else:
      print("{}This router has no port.".format(' '*2))

    print("")


  def inspect_network_connector(network_connector):
    """ネットワークコネクタの中身を確認します"""

    nc = network_connector
    print("Network Connector {}".format(nc.get('name', 'NO NAME')))
    print("{}UUID is {}".format(' '*2, nc.get('id')))
    print("{}Pool uuid is {}".format(' '*2, nc.get('network_connector_pool_id')))
    print("{}Tenant uuid is {}".format(' '*2, nc.get('tenant_id')))

    # このコネクタに付属するエンドポイント
    network_connector_endpoints = nc.get('network_connector_endpoints', [])
    if network_connector_endpoints:
      for ncep_id in network_connector_endpoints:
        ncep = get_network_connector_endpoint_by_id(ncep_id)
        print("{}Network Connector Endpoint {}".format(' '*2, ncep.get('name')))
        print("{}Ncep uuid is {}".format(' '*4, ncep.get('id')))
        print("{}Type is {}".format(' '*4, ncep.get('endpoint_type')))
        print("{}Tenant uuid is {}".format(' '*4, ncep.get('tenant_id')))
        print("{}Location is {}".format(' '*4, ncep.get('location')))
        # このコネクタエンドポイントが持つポートの情報を表示したい
        # ポートのdevice_idキーは、内部の意味不明な物になってしまうため、対応付けがとれない
        # そのためにk5-list-connected-interfaces-of-network-connector-endpoint.pyの情報を使う
        # {
        #   "network_connector_endpoint": {
        #     "interfaces": [
        interface_list = ncep.get('interfaces', [])
        for iface in interface_list:
          port_id = iface.get('port_id')
          port = get_port_by_id(port_id)
          if port:
            name = port.get('name')
            if not name:
              name = 'NO-NAME'
            print("{}Port {} is {}, Admin state is {}".format(' '*4, name, port.get('status'), port.get('admin_state_up')))
            print("{}Port uuid is {}".format(' '*6, port.get('id', '')))
            print("{}Port is attached to the Network {}".format(' '*6, port.get('network_id', '')))
            print("{}binding:vnic_type is {}".format(' '*6, port.get('binding:vnic_type')))
            print("{}Hardware address is {}".format(' '*6, port.get('mac_address')))
            for fixedip in port.get('fixed_ips', []):
              print("{}Internet address is {} , Subnet is {}".format(' '*6, fixedip.get('ip_address'), fixedip.get('subnet_id')))

    else:
      print("{}This network connector has no endpoint.".format(' '*2))

    print("")


  def inspect_network(network):
    """ネットワークの中身を確認します"""

    n = network
    print("Network {} is {}, Admin state is {}".format(n.get('name', 'NO NAME'), n.get('status'), n.get('admin_state_up')))
    print("{}UUID is {}".format(' '*2, n.get('id')))
    print("{}External is {}".format(' '*2, n.get('router:external')))
    print("{}Shared is {}".format(' '*2, n.get('shared')))
    print("{}Tenant uuid is {}".format(' '*2, n.get('tenant_id')))
    print("{}Availability zone is {}".format(' '*2, n.get('availability_zone')))

    # サブネットを表示
    for subnet_id in n.get('subnets'):
      subnet = get_subnet_by_id(subnet_id)
      if not subnet:
        print("{}Subnet uuid is {}".format(' '*2, subnet_id))
        continue
      print("{}Subnet {} is {}".format(' '*2, subnet.get('name', 'NO NAME'), subnet.get('id')))
      print("{}Internet address is {}".format(' '*4, subnet.get('cidr')))
      print("{}Gateway is {}".format(' '*4, subnet.get('gateway_ip')))
      print("{}DHCP is {}".format(' '*4, subnet.get('enable_dhcp')))
      dns_nameservers = subnet.get('dns_nameservers')
      if dns_nameservers:
        print("{}DNS nameservers".format(' '*4))
        for nameserver in dns_nameservers:
          print("{}{}".format(' '*6, nameserver))
      else:
        print("{}DNS nameserver is not set.".format(' '*4))
      host_routes = subnet.get('host_routes')
      if host_routes:
        print("{}Host routes".format(' '*4))
        for route in host_routes:
          print("{}{} via {}".format(' '*6, route.get('destination'), route.get('nexthop')))
      else:
        print("{}Host routes is not set.".format(' '*4))

    # ポートを表示
    ports = search_port_by_network_id(n.get('id'))
    if ports:
      for port in ports:
        name = port.get('name')
        if not name:
          name = 'NO-NAME'
        print("{}Port {} is {}, Admin state is {}".format(' '*2, name, port.get('status'), port.get('admin_state_up')))
        print("{}Port uuid is {}".format(' '*4, port.get('id', '')))
        print("{}binding:vnic_type is {}".format(' '*4, port.get('binding:vnic_type')))
        print("{}Hardware address is {}".format(' '*4, port.get('mac_address')))
        for fixed_ip in port.get('fixed_ips', []):
          print("{}Internet address is {} ,Subnet is {}".format(' '*4, fixed_ip.get('ip_address'), fixed_ip.get('subnet_id')))
        device_owner = port.get('device_owner')
        if device_owner:
          print("{}Device owner is {}".format(' '*4, device_owner))
          print("{}Device id is {}".format(' '*4, port.get('device_id')))
        else:
          print("{}Device owner is not set.".format(' '*4))
    else:
      print("{}This network has no port.".format(' '*2))

    print("")


  def get_list(key):
    """k5-list-xxxの結果の配列をdbから取り出して返します"""
    obj = db.get(q[key].exists())
    value = obj.get(key, [])
    if not value:
      value = []
    return value


  def exists_in(nodes, target_id):
    """nodes配列にtarget_idを持ったオブジェクトが存在する場合はTrue"""
    if list(filter(lambda x: x.get(id) == target_id, nodes)):
      return True
    return False


  def generate_topology_data():
    """描画用のトポロジデータを作成します"""

    # リンク配列
    # sourceとtargetで何と何がつながっているかを表す
    links = []

    # ノード配列
    nodes = []

    # 全ルータをチェック
    routers = get_list('routers')
    for router in routers:
      router['node_type'] = 'ROUTER'
      router['x'] = 10
      router['y'] = 10
      nodes.append(router)
      router_id = router.get('id')
      eginfo = router.get('external_gateway_info', {})
      if eginfo:
        network_id = eginfo.get('network_id')
        network = get_network_by_id(network_id)
        network['node_type'] = 'NETWORK'
        network['x'] = 20
        network['y'] = 20
        if not exists_in(nodes, network_id):
          nodes.append(network)
          links.append({'source': router_id, 'target': network_id})
      # このルータを親にしているポートを探す
      port_list = search_port_by_device_id(router_id)
      for port in port_list:
        port_id = port.get('id')
        if not exists_in(nodes, port_id):
          port['node_type'] = 'PORT'
          port['x'] = 30
          port['y'] = 30
          nodes.append(port)
          links.append({'source': router_id, 'target': port_id})
          network_id = port.get('network_id')
          network = get_network_by_id(network_id)
          if not exists_in(nodes, network_id):
            network['node_type'] = 'NETWORK'
            network['x'] = 40
            network['y'] = 40
            nodes.append(network)
            links.append({'source': port_id, 'target': network_id})

    # 全コネクタエンドポイントをチェック
    ncep_list = get_list('network_connector_endpoints')
    for ncep in ncep_list:
      ncep_id = ncep.get('id')
      ncep['node_type'] = 'NCEP'
      ncep['x'] = 50
      ncep['y'] = 50
      nodes.append(ncep)
      # 親となるネットワークコネクタ
      network_connector_id = ncep.get('network_connector_id')
      nc = get_network_connector_by_id(network_connector_id)
      nc_id = nc.get('id')
      if not exists_in(nodes, nc_id):
        nc['node_type'] = 'NC'
        nc['x'] = 60
        nc['y'] = 60
        nodes.append(nc)
        links.append({'source': ncep_id, 'target': nc_id})
        # ネットワークコネクタの親になるコネクタプール
        ncp_id = nc.get('network_connector_pool_id')
        ncp = get_network_connector_pool_by_id(ncp_id)
        ncp_id = ncp.get('id')
        if not exists_in(nodes, ncp_id):
          ncp['node_type'] = 'NCPOOL'
          ncp['x'] = 70
          ncp['y'] = 70
          nodes.append(ncp)
          links.append({'source': nc_id, 'target': ncp_id})

      # 子となる接続ポート
      interface_list = ncep.get('interfaces', [])
      for iface in interface_list:
        port_id = iface.get('port_id')
        port = get_port_by_id(port_id)
        if not filter(lambda x: x.get(id) == port_id, nodes):
          port['node_type'] = 'PORT'
          port['x'] = 80
          port['y'] = 80
          nodes.append(port)
          links.append({'source': ncep_id, 'target': port_id})

    # 全ネットワークコネクタをチェック
    nc_list = get_list('network_connectors')
    for nc in nc_list:
      nc_id = nc.get('id')
      if not filter(lambda x: x.get(id) == nc_id, nodes):
        nc['node_type'] = 'NC'
        nc['x'] = 90
        nc['y'] = 90
        nodes.append(nc)

    # 全ポートをチェックする
    port_list = get_list('ports')
    for port in port_list:
      port_id = port.get('id')
      if not filter(lambda x: x.get(id) == port_id, nodes):
        port['node_type'] = 'PORT'
        port['x'] = 100
        port['y'] = 100
        nodes.append(port)
        network_id = port.get('network_id')
        network = get_network_by_id(network_id)
        if not filter(lambda x: x.get(id) == network_id, nodes):
          network['node_type'] = 'NETWORK'
          network['x'] = 110
          network['y'] = 110
          nodes.append(network)
          links.append({'source': port_id, 'target': network_id})

    # 全ネットワークをチェックする
    network_list = get_list('networks')
    for network in network_list:
      if 'inf_' in network.get('name', ''):
        continue
      network_id = network.get('id')
      if not filter(lambda x: x.get(id) == network_id, nodes):
        network['node_type'] = 'NETWORK'
        network['x'] = 120
        network['y'] = 120
        nodes.append(network)
        port_list = search_port_by_network_id(network_id)
        for port in port_list:
          port_id = port.get('id')
          if not filter(lambda x: x.get(id) == port_id, nodes):
            port['node_type'] = 'PORT'
            port['x'] = 130
            port['y'] = 130
            nodes.append(port)
            links.append({'source': network_id, 'target': port_id})

    # JSON形式で表示
    json_str = json.dumps({'nodes': nodes, 'links': links}, indent=2)
    print(json_str)

    save_as_javascript(json_str)


  def save_as_javascript(json_str):
    """JavaScriptファイルとして保存"""
    js_header = '''
/*global d3iida*/

d3iida.heredoc.topology = (function () {
  var text = function() {/*EOF*
  '''

    js_footer = '''
  *EOF*/}.toString().replace(/(\\n)/g, '').split('*EOF*')[1];
  return {
    text : text,
    data : JSON.parse(text)
  };
}());
    '''

    # JavaScriptファイルを出力する
    filename = 'd3iida.heredoc.topology.js'
    path = os.path.join(app_home, 'data', filename)

    with codecs.open(path, mode="w", encoding="utf_8") as f:
      f.write(js_header + json_str + js_footer)



  def main():
    """メイン"""

    if args.create:
      return create_cache()

    if args.generate:
      generate_topology_data()

    if args.router:
      routers = get_list('routers')
      if routers:
        routers = sorted(routers, key=lambda x: x.get('name', ''))
        for router in routers:
          inspect_router(router)

    if args.network_connector:
      connectors = get_list('network_connectors')
      if connectors:
        connectors = sorted(connectors, key=lambda x: x.get('name', ''))
        for connector in connectors:
          inspect_network_connector(connector)

    if args.network:
      networks = get_list('networks')
      if networks:
        networks = sorted(networks, key=lambda x: x.get('name', ''))
        for network in networks:
          if 'inf_' in network.get('name'):
            continue
          inspect_network(network)

    if args.dump:
      print(json.dumps(db.all(), indent=2))

    return 0


  # 実行
  sys.exit(main())
