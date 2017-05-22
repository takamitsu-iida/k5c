#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POST /v2.0/floatingips
Create floating IP
Floating IPを作成する。ポート情報を指定した場合にはポートとFloating IPを関連づける。

NOTE:
　・ルータにはexternal_gateway_infoがセットされていないといけない？？？
"""

"""
実行例

ネットワークIDは事業者が用意している外部ネットワークを指定する。複数あるので、良さそうなものをチョイスする。

inf_az1_ext-net05
cd4057bd-f72e-4244-a7dd-1bcb2775dd67

内側のサブネットの名前
iida-az1-subnet01

内側のサブネットのID
abbbbcf4-ea8f-4218-bbe7-669231eeba30

内側のポートは新規に作成する（固定IPを持たせる）

./bin/k5-create-port.py \
--name iida-az1-net01-port02 \
--network-id 8f15da62-c7e5-47ec-8668-ee502f6d00d2 \
--subnet-id abbbbcf4-ea8f-4218-bbe7-669231eeba30 \
--ip-address 10.1.1.100

POST /v2.0/ports
=================  ====================================
name               iida-az1-net01-port02
id                 77297e3a-7135-4fb4-8024-e677d9df66d4
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         8f15da62-c7e5-47ec-8668-ee502f6d00d2
binding:vnic_type  normal
mac_address        fa:16:3e:43:b2:f6
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.1.100    abbbbcf4-ea8f-4218-bbe7-669231eeba30
============  ====================================
bash-4.4$


フローティングIPを作成する

bash-4.4$ ./bin/k5-create-floatingip.py \
> --network-id cd4057bd-f72e-4244-a7dd-1bcb2775dd67 \
> --port-id 77297e3a-7135-4fb4-8024-e677d9df66d4 \
> --fixed-ip 10.1.1.100
POST /v2.0/floatingips
===================  ====================================
id                   5654254d-0f36-425d-ae89-6e827fc99e54
floating_ip_address  133.162.215.230
fixed_ip_address     10.1.1.100
status               DOWN
port_id              77297e3a-7135-4fb4-8024-e677d9df66d4
router_id            ffbd70be-24cf-4dff-a4f6-661bf892e313
availability_zone    jp-east-1a
tenant_id            a5001a8b9c4a4712985c11377bd6d4fe
===================  ====================================
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
# リクエストデータを作成する
#
def make_request_data(network_id="", fixed_ip="", port_id="", tenant_id="", az=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  # 作成するフローティングのオブジェクト
  floatingip_object = {
    'floating_network_id': network_id
  }

  if fixed_ip:
    floatingip_object['fixed_ip_address'] = fixed_ip

  if port_id:
    floatingip_object['port_id'] = port_id

  if tenant_id:
    floatingip_object['tenant_id'] = tenant_id

  if az:
    floatingip_object['availability_zone'] = az

  return {'floatingip': floatingip_object}


#
# APIにアクセスする
#
def access_api(data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK + "/v2.0/floatingips"

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # POSTメソッドで作成して、結果のオブジェクトを得る
  r = c.post(url=url, data=data)

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

  # フローティングIPの情報はデータオブジェクトの中の'floatingip'キーにオブジェクトとして入っている
  #{
  #  "data": {
  #    "floatingip": {
  #      "floating_ip_address": "133.162.215.224",
  #      "status": "DOWN",
  #      "id": "6254e6f4-e3bb-4824-a390-110a883d4281",
  #      "fixed_ip_address": "10.1.1.100",
  #      "port_id": "77297e3a-7135-4fb4-8024-e677d9df66d4",
  #      "availability_zone": "jp-east-1a",
  #      "floating_network_id": "cd4057bd-f72e-4244-a7dd-1bcb2775dd67",
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "router_id": "ffbd70be-24cf-4dff-a4f6-661bf892e313"
  #    }
  #  },
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 201
  #}
  fip = data.get('floatingip', {})

  disp_keys = ['id', 'floating_ip_address', 'fixed_ip_address', 'status', 'port_id', 'router_id', 'availability_zone', 'tenant_id']

  # 表示用に配列にする
  fip_list = []
  for key in disp_keys:
    fip_list.append([key, fip.get(key, '')])

  # 表示
  print("/v2.0/floatingips")
  print(tabulate(fip_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Creates a floating IP')
    parser.add_argument('--network-id', dest='network_id', metavar='id', required=True, help='The ID of the network associated with the floating IP.')
    parser.add_argument('--fixed-ip', dest='fixed_ip', metavar='addr', nargs='?', help='The fixed IP address associated with the floating IP.')
    parser.add_argument('--port-id', dest='port_id', metavar='id', nargs='?', help='The port ID.')
    parser.add_argument('--tenant-id', dest='tenant_id', metavar='id', nargs='?', default=k5c.TENANT_ID, help='The tenant ID. default: {}'.format(k5c.TENANT_ID))
    parser.add_argument('--az', nargs='?', default=k5c.AZ, help='The Availability Zone name. default: {}'.format(k5c.AZ))
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    network_id = args.network_id
    fixed_ip = args.fixed_ip
    port_id = args.port_id
    tenant_id = args.tenant_id
    az = args.az
    dump = args.dump

    # リクエストデータを作成
    data = make_request_data(network_id=network_id, fixed_ip=fixed_ip, port_id=port_id, tenant_id=tenant_id, az=az)
    # print(json.dumps(data, indent=2))


    # 実行
    result = access_api(data=data)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 得たデータを処理する
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
