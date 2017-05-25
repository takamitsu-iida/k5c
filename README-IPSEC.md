# IPsecを使う場合のメモ

実際に動かしたわけではないので、良くわからない部分も多い。

取り急ぎ、メモ。


## 注意事項

- Router：VPN Service：SiteConnection＝１：１：Ｎ

- IPsecからIPsecへの折り返しの通信はできない

- デフォルトでスプリットトンネルされている

- フラグメントはダメなので対向ルータでTCP MSSを小さく書き換えること

> NOTE*
>
> K5間のIPsecの場合、フラグメントはどうしてるんだろう？？？


## VPNサービスの作成に必要な情報

VPNサービスを作成するには、ルータIDとサブネットIDが必要。

- router_id
- subnet_id

## IKEポリシーの作成に必要な情報

IKEポリシーを作成するには、名前の他にIKEのパラメータが必要

- name
- ikepolicy

## IPsecポリシーの作成に必要な情報

IPsecポリシーを作成するには、名前の他にIPsecのパラメータが必要

- name
- ipsecpolicy

## IPsecコネクションの作成に必要な情報

これが一番重要。最大20コネクションまで別々に作成する。

- ikepolicy_id
- ipsec_site_connection
  - name
  - vpnservice_id
  - ipsecpolicy_id
  - peer_address
  - peer_cidrs


# 下準備

<BR>

## ルータの情報収集

ルータの一覧。ルータは一つ作成済み。

```
bash-4.4$ ./bin/k5-list-routers.py
GET /v2.0/routers
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
ffbd70be-24cf-4dff-a4f6-661bf892e313  iida-az1-router01  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========
bash-4.4$
```

ルータの詳細情報。

```
bash-4.4$ ./bin/k5-list-routers.py | ./bin/k5-show-router.py -
ffbd70be-24cf-4dff-a4f6-661bf892e313
GET /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================

external_gateway_info
===========  ====================================
enable_snat  True
network_id   cd4057bd-f72e-4244-a7dd-1bcb2775dd67
===========  ====================================

routes
==============  =========
destination     nexthop
==============  =========
10.0.0.0/8      10.1.2.9
172.16.0.0/12   10.1.2.9
192.168.0.0/16  10.1.2.9
==============  =========

bash-4.4$
```

ルータの情報を整理するとこうなります。
外部ネット(external_gateway_info)が存在しない場合は、bin/k5-update-router.pyで外部のネットワークを紐付けてください。

|name|router_id|外部ネット|
|:--|:--|:--|
|iida-az1-router01|ffbd70be-24cf-4dff-a4f6-661bf892e313|cd4057bd-f72e-4244-a7dd-1bcb2775dd67|

<BR>

## 内部ネットワークの情報収集

内部ネットワークの一覧。

```
bash-4.4$ ./bin/k5-list-networks.py | grep -v inf_
GET /v2.0/networks
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
8f15da62-c7e5-47ec-8668-ee502f6d00d2  iida-az1-net01     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
e3c166c0-7e90-4c6e-857e-87fd985f98ac  iida-az1-net02     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========
bash-4.4$
```

-net01の詳細情報。

```
bash-4.4$ ./bin/k5-list-networks.py | grep iida-az1-net01 | ./bin/k5-show-network.py -
8f15da62-c7e5-47ec-8668-ee502f6d00d2
GET /v2.0/networks/{network_id}
==============  ====================================  ==========  ========
name            id                                    az          status
==============  ====================================  ==========  ========
iida-az1-net01  8f15da62-c7e5-47ec-8668-ee502f6d00d2  jp-east-1a  ACTIVE
==============  ====================================  ==========  ========

====================================
subnets
====================================
abbbbcf4-ea8f-4218-bbe7-669231eeba30
====================================

bash-4.4$
```

-net02の詳細情報。

```
bash-4.4$ ./bin/k5-list-networks.py | grep iida-az1-net02 | ./bin/k5-show-network.py -
e3c166c0-7e90-4c6e-857e-87fd985f98ac
GET /v2.0/networks/{network_id}
==============  ====================================  ==========  ========
name            id                                    az          status
==============  ====================================  ==========  ========
iida-az1-net02  e3c166c0-7e90-4c6e-857e-87fd985f98ac  jp-east-1a  ACTIVE
==============  ====================================  ==========  ========

====================================
subnets
====================================
2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
====================================

bash-4.4$
```

ネットワークの情報を整理するとこのようになります。
必要なのはネットワークIDではなく、サブネットIDの方です。

|ネットワーク名|subnet_id|
|:--|:--|
|net01|abbbbcf4-ea8f-4218-bbe7-669231eeba30|
|net02|2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6|

<BR>

## ポートの情報を調べる

デバイスオーナーがnetwork:router_interfaceになっているものは、ルータにくっついたポートです。
ルータには固定のIPアドレスを振っていると思うので、アドレスをみればどのルータについているか分かるでしょう。

```
bash-4.4$ ./bin/k5-list-ports.py | ./bin/k5-show-port.py -
port_id: 689d24c7-02a2-4dfd-b809-9ad4060e079f
GET /v2.0/ports/{port_id}
=================  ====================================
name               iida-az1-net01-port01
id                 689d24c7-02a2-4dfd-b809-9ad4060e079f
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             ACTIVE
admin_state_up     True
device_owner       network:router_interface
device_id          ffbd70be-24cf-4dff-a4f6-661bf892e313
network_id         8f15da62-c7e5-47ec-8668-ee502f6d00d2
binding:vnic_type  normal
mac_address        fa:16:3e:84:72:35
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.1.1      abbbbcf4-ea8f-4218-bbe7-669231eeba30
============  ====================================

port_id: 74233502-90d1-47f7-976e-f3def361d2a1
GET /v2.0/ports/{port_id}
=================  ====================================
name               iida-az1-net02-port02
id                 74233502-90d1-47f7-976e-f3def361d2a1
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             ACTIVE
admin_state_up     True
device_owner       network:router_interface
device_id          dfceb849-0c47-4fcd-a583-757628898501
network_id         e3c166c0-7e90-4c6e-857e-87fd985f98ac
binding:vnic_type  normal
mac_address        fa:16:3e:2a:5a:58
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.2.9      2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
============  ====================================

port_id: bdab1ca6-fd32-4729-9e97-3827b72d7bc5
GET /v2.0/ports/{port_id}
=================  ====================================
name               iida-az1-net02-port01
id                 bdab1ca6-fd32-4729-9e97-3827b72d7bc5
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             ACTIVE
admin_state_up     True
device_owner       network:router_interface
device_id          ffbd70be-24cf-4dff-a4f6-661bf892e313
network_id         e3c166c0-7e90-4c6e-857e-87fd985f98ac
binding:vnic_type  normal
mac_address        fa:16:3e:ea:73:57
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.2.1      2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
============  ====================================

bash-4.4$
```

IPアドレスが3個見えます。

10.1.1.1はnet01についたルータのアドレス、10.1.2.1はnet02についたルータのアドレス、10.1.2.9はネットワークコネクタのアドレスです。

ここでは、net01上の10.1.1.1のアドレスを持つポートにフローティングIPを割り当てます。

このルータに紐付いている外部ネットからグローバルIPをとってくるようにします。

```
bash-4.4$ ./bin/k5-create-floatingip.py \
> --network-id cd4057bd-f72e-4244-a7dd-1bcb2775dd67 \
> --port-id 689d24c7-02a2-4dfd-b809-9ad4060e079f \
> --fixed-ip 10.1.1.1

/v2.0/floatingips
===================  ====================================
id                   30627d45-37dd-4e76-9200-61834035229f
floating_ip_address  133.162.215.250
fixed_ip_address     10.1.1.1
status               DOWN
port_id              689d24c7-02a2-4dfd-b809-9ad4060e079f
router_id            ffbd70be-24cf-4dff-a4f6-661bf892e313
availability_zone    jp-east-1a
tenant_id            a5001a8b9c4a4712985c11377bd6d4fe
===================  ====================================
```

statusがDOWNからACTIVEに変わるのに、しばらく時間がかかるようです。

<BR>

## YAMLファイルに設定を書く

このファイルを使います。

- conf/ipsec.yaml

<BR>

## ファイアウォールでIPsec通信を許可する

> NOTE:
>
> IPsecの通信をファイアウォールで許可する場合はグローバルIPを使ってルールを作成するみたい。まぁ、自装置宛てだからNAT変換されないしね。
> アドレスはsourceとdestinationの両方を指定すればいいのかな。
> この場合プロトコルはnullだとまずいのかな。
> espだからtcpでもudpでもicmpでもないし。

使うのはこれら。

- bin/k5-create-fw-rule.py
- bin/k5-update-fw-policy.py
- conf/fw-rule.xlsx

エクセルでルールを作成して、k5-create-fw-rule.pyで作成。
エクセルでルールの並びとかを調整して、k5-update-fw-policy.pyで更新します。

<BR>
<BR>
<BR>

# IPsec VPNを作成する

<BR>

## vpnserviceを作成する


- conf/ipsec.yaml

YAMLのキーは作成したいVPNサービスの名前にする

```yaml
#
# /v2.0/vpn/vpnservices
#
iida-az1-vpnservice:

  vpnservice:

    # 名前
    name: iida-az1-vpnservice

    # ルータID
    router_id: ffbd70be-24cf-4dff-a4f6-661bf892e313

    # サブネットID
    subnet_id: abbbbcf4-ea8f-4218-bbe7-669231eeba30

    # アベイラビリティゾーン
    # jp-east-1a
    # jp-east-1b
    availability_zone: jp-east-1a
```

この名前を指定して、作成する。

- bin/k5-create-vpnservice.py

```
bash-4.4$ ./bin/k5-create-vpnservice.py --name iida-az1-vpnservice
=================  ====================================
id                 75f35f53-ecbd-4748-a070-3316435e35cc
name               iida-az1-vpnservice
availability_zone  jp-east-1a
=================  ====================================
```


<BR>

## IKEポリシーの作成

- conf/ipsec.yaml

キーに名前作りたい名前を指定する。

```yaml
#
# /v2.0/vpn/ikepolicies
#
iida-az1-ikepolicy:

  ikepolicy:

    # 名前
    name: iida-az1-ikepolicy

    # IKEバージョン
    ike_version: v1

    # メインモード
    phase1_negotiation_mode: main

    # 認証
    auth_algorithm: sha1

    # 暗号
    encryption_algorithm: aes-256

    # PFS
    pfs: group14

    # ライフタイム
    lifetime:
      units: seconds
      value: 86400

    # アベイラビリティゾーン
    # jp-east-1a
    # jp-east-1b
    availability_zone: jp-east-1a
```

この名前を指定して、作成する。

- bin/k5-create-ikepolicy.py

```
bash-4.4$ ./bin/k5-create-ikepolicy.py --name iida-az1-ikepolicy
POST /v2.0/vpn/ikepolicies
=======================  ====================================
name                     iida-az1-ikepolicy
id                       c6f42ec6-e76d-48ff-a6a6-9b86288381de
auth_algorithm           sha1
pfs                      group14
ike_version              v1
encryption_algorithm     aes-256
phase1_negotiation_mode  main
tenant_id                a5001a8b9c4a4712985c11377bd6d4fe
availability_zone        jp-east-1a
=======================  ====================================
bash-4.4$
```

<BR>

## IPsecポリシーの作成

- conf/ipsec.yaml

キーに名前作りたい名前を指定する。

```yaml
#
# /v2.0/vpn/ipsecpolicies
#
iida-az1-ipsecpolicy:

  ipsecpolicy:

    # 名前
    name: iida-az1-ipsecpolicy

    # トランスフォーム
    transform_protocol: esp

    # 認証
    auth_algorithm: sha1

    # カプセル化
    encapsulation_mode: tunnel

    # 暗号アルゴリズム
    encryption_algorithm: aes-256

    # PFS
    pfs: group14

    # ライフタイム
    lifetime:
      units: seconds
      value: 28800

    # アベイラビリティゾーン
    # jp-east-1a
    # jp-east-1b
    availability_zone: jp-east-1a
```

この名前を指定して、作成する。

- bin/k5-create-ipsecpolicy.py

```
bash-4.4$ ./bin/k5-create-ipsecpolicy.py --name iida-az1-ipsecpolicy
POST /v2.0/vpn/ipsecpolicies
====================  ====================================
name                  iida-az1-ipsecpolicy
id                    26525271-0337-4ad2-b0d3-120814fc0794
pfs                   group14
auth_algorithm        sha1
encryption_algorithm  aes-256
transporm_protocol
tenant_id             a5001a8b9c4a4712985c11377bd6d4fe
availability_zone     jp-east-1a
====================  ====================================
```

<BR>

## サイトトンネルの作成

- conf/ipsec.yaml

キーに名前作りたい名前を指定する。

```yaml
#
# /v2.0/vpn/ipsec-site-connections
#
iida-az1-connection-01:

  ipsec_site_connection:

    name: iida-az1-connection-01

    # ★
    # 相手毎に設定
    psk: passpass

    # ★
    # 相手毎に設定
    peer_cidrs:
      - 10.2.1.0/24

    # ★
    # 相手のグローバルIP
    peer_address: 2.2.2.2

    # ★
    # 相手を識別する情報
    # 基本はpeer_addressと同じ
    peer_id: 2.2.2.2

    # ★
    # bin/k5-list-vpnservices.py
    vpnservice_id: 75f35f53-ecbd-4748-a070-3316435e35cc

    # ★
    # bin/k5-list-ikepolicy.py
    ikepolicy_id: 9fc16042-95ae-46b9-84bc-4777b3b9f89c

    # ★
    # bin/k5-list-ipsecpolicy.py
    ipsecpolicy_id: 26525271-0337-4ad2-b0d3-120814fc0794

    admin_state_up: True

    initiator: bi-directional

    mtu: 1500

    dpd:
      timeout: 30
      interval: 10
      action: restart

    # アベイラビリティゾーン
    # jp-east-1a
    # jp-east-1b
    availability_zone: jp-east-1a
```

この名前を指定して作成する。

- bin/k5-create-site-connection.py

```
bash-4.4$ ./bin/k5-create-site-connection.py --name iida-az1-connection-01
POST /v2.0/vpn/ipsec-site-connections
=================  ====================================
name               iida-az1-connection-01
id                 4273f817-da1c-4aa5-9445-6501d5bed29d
peer_address       2.2.2.2
peer_id            2.2.2.2
psk                passpass
vpnservice_id      75f35f53-ecbd-4748-a070-3316435e35cc
ikepolicy_id       9fc16042-95ae-46b9-84bc-4777b3b9f89c
ipsecpolicy_id     26525271-0337-4ad2-b0d3-120814fc0794
route_mode         static
mtu                1500
initiator          bi-directional
auth_mode          psk
status             PENDING_CREATE
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
availability_zone  jp-east-1a
description
=================  ====================================
bash-4.4$
```
