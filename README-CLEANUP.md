# K5環境を撤収するときのメモ

全てを削除するにしても手順が大事です。
利用中のものを削除しようとしてもエラーが返ってきて削除できません。
削除する場合も親子関係を理解しておく必要があります。

<BR>

## IPsecの削除

IPsecトンネルが存在するか、確認します。

```
bash-4.4$ ./bin/k5-list-site-connections.py
GET /v2.0/vpn/ipsec-site-connections
====================================  ======================  ===============  ========  ===================
id                                    name                    peer_address     status    availability_zone
====================================  ======================  ===============  ========  ===================
95a24cec-01f9-4128-9034-21dd1c9e4ea7  iida-az1-connection-01  133.162.223.232  ACTIVE    jp-east-1a
66762a0e-488d-4286-86a1-e8b8db1ca9e0  iida-az2-connection-01  133.162.215.250  ACTIVE    jp-east-1b
====================================  ======================  ===============  ========  ===================
```

存在する場合は削除します。
思い残すことがなければ一括で削除しましょう。
これ以降IPsecトンネルを経由した通信はできなくなります。

```
bash-4.4$ ./bin/k5-list-site-connections.py | ./bin/k5-delete-site-connection.py -
connection_id: 95a24cec-01f9-4128-9034-21dd1c9e4ea7
status_code: 204


connection_id: 66762a0e-488d-4286-86a1-e8b8db1ca9e0
status_code: 204
```

サイトコネクションがなくなったら、あとは不要なコンフィグですので削除していきましょう。
IPsecポリシーを表示します。

```
bash-4.4$ ./bin/k5-list-ipsecpolicy.py
GET /v2.0/vpn/ipsecpolicies
====================================  ====================  ================================  ===================
id                                    name                  tenant_id                         availability_zone
====================================  ====================  ================================  ===================
ab659e26-327b-4aff-b727-b039da09f22e  iida-az1-ipsecpolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
375f5750-6e84-4674-98c4-47e24aaa3acf  iida-az2-ipsecpolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b
====================================  ====================  ================================  ===================
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-ipsecpolicy.py | ./bin/k5-delete-ipsecpolicy.py -
ipsecpolicy_id: ab659e26-327b-4aff-b727-b039da09f22e
status_code: 204


ipsecpolicy_id: 375f5750-6e84-4674-98c4-47e24aaa3acf
status_code: 204
```

IKEポリシーを表示します。

```
bash-4.4$ ./bin/k5-list-ikepolicy.py
GET /v2.0/vpn/ikepolicies
====================================  ==================  ================================  ===================
id                                    name                tenant_id                         availability_zone
====================================  ==================  ================================  ===================
4334b806-824c-4419-b0cb-b79fa8be9c72  iida-az1-ikepolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
8dcb5c2b-f39e-4a4b-a6ed-4413528effb5  iida-az2-ikepolicy  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b
====================================  ==================  ================================  ===================
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-ikepolicy.py | ./bin/k5-delete-ikepolicy.py -
ikepolicy_id: 4334b806-824c-4419-b0cb-b79fa8be9c72
status_code: 204

ikepolicy_id: 8dcb5c2b-f39e-4a4b-a6ed-4413528effb5
status_code: 204
```

VPNサービスを表示します。

```
bash-4.4$ ./bin/k5-list-vpnservices.py
GET /v2.0/vpn/vpnservices
====================================  ===================  ===================
id                                    name                 availability_zone
====================================  ===================  ===================
37ab0e56-1ff1-4dbe-acce-fd7ed1a3773a  iida-az1-vpnservice  jp-east-1a
b121c00b-c198-490f-8304-99687f0022df  iida-az2-vpnservice  jp-east-1b
====================================  ===================  ===================
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-vpnservices.py | ./bin/k5-delete-vpnservice.py -
vpnservice_id: 37ab0e56-1ff1-4dbe-acce-fd7ed1a3773a
status_code: 204

vpnservice_id: b121c00b-c198-490f-8304-99687f0022df
status_code: 204
```

<BR>

## フローティングIPを返却する

フローティングIPが存在するか確認します。

```
bash-4.4$ ./bin/k5-list-floatingips.py
/v2.0/floatingips
====================================  =====================  ==================  ========  ===================
id                                    floating_ip_address    fixed_ip_address    status    availability_zone
====================================  =====================  ==================  ========  ===================
30627d45-37dd-4e76-9200-61834035229f  133.162.215.250        10.1.1.1            ACTIVE    jp-east-1a
13320826-9d89-4ed2-a69b-6aec369fcd8e  133.162.223.232        10.2.1.1            ACTIVE    jp-east-1b
====================================  =====================  ==================  ========  ===================
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-floatingips.py | ./bin/k5-delete-floatingip.py -
status_code: 204

status_code: 204

bash-4.4$
```

<BR>

## ファイアウォールの削除

ファイアウォールが存在するか確認します。

```
bash-4.4$ ./bin/k5-list-firewalls.py
/v2.0/fw/firewalls
====================================  =============  ====================================  ====================================  ========
id                                    name           router_id                             firewall_policy_id                    status
====================================  =============  ====================================  ====================================  ========
94b21ac8-1890-417a-a2de-515ec0a009d6  iida-az1-fw01  ffbd70be-24cf-4dff-a4f6-661bf892e313  3e500de7-5d7c-4585-954f-f911e077fa58  ACTIVE
f439c2c5-f2e8-4f9b-94bc-72303fe160c2  iida-az2-fw01  c97f9aa5-eacc-48ae-b5df-82784bce8b63  9a9484c1-bdea-434f-8e59-755b41dbb12f  ACTIVE
====================================  =============  ====================================  ====================================  ========
```

一括で削除します。
削除するとファイアウォールが機能しなくなります。

```
bash-4.4$ ./bin/k5-list-firewalls.py | ./bin/k5-delete-firewall.py -
94b21ac8-1890-417a-a2de-515ec0a009d6
status_code: 204

f439c2c5-f2e8-4f9b-94bc-72303fe160c2
status_code: 204
```

ファイアウォールポリシーが存在するか確認します。

```
bash-4.4$ ./bin/k5-list-fw-policies.py
GET /v2.0/fw/firewall_policies
====================================  ======  ==============  ================================  ==========
id                                    name      num of rules  tenant_id                         az
====================================  ======  ==============  ================================  ==========
9a9484c1-bdea-434f-8e59-755b41dbb12f  all                 12  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b
3e500de7-5d7c-4585-954f-f911e077fa58  all                 14  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ======  ==============  ================================  ==========
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-fw-policies.py | ./bin/k5-delete-fw-policy.py -
9a9484c1-bdea-434f-8e59-755b41dbb12f
status_code: 204


3e500de7-5d7c-4585-954f-f911e077fa58
status_code: 204
```

ファイアウォールルールを確認します。

```
bash-4.4$ ./bin/k5-list-fw-rules.py
policy : unused
====================================  =============================  ==========  ========  ==========  ===================
id                                    name                           position    action    protocol    availability_zone
====================================  =============================  ==========  ========  ==========  ===================
0d7d84d9-3b64-4d6e-8aa9-e2276073321b  deny-all-tcp                               deny      tcp         jp-east-1b
0f2a1d89-676f-4741-8bf3-5c8a72794212  iida-az2-p01-net01-any-tcp                 allow     tcp         jp-east-1b
1cabdeee-6835-4727-940f-57eb0a3cef04  iida-az2-p01-net01-any-icmp                allow     icmp        jp-east-1b
28e4a83c-8580-466b-8ffa-3e67b7f5e520  iida-az2-p01-net01-any-udp                 allow     udp         jp-east-1b
2ba9dca6-8e3f-4a2f-867a-71e7e6b74f2f  iida-az2-p01-net01-net02-udp               deny      udp         jp-east-1b
66d1ab16-ec6c-40d4-8b2d-64a92319757c  iida-az2-p01-net01-net02-icmp              deny      icmp        jp-east-1b
ab470fe0-d3e0-4f5f-8f28-eb6de66fd3e3  deny-all-udp                               deny      udp         jp-east-1b
b338b0b9-dc57-4d10-b5cf-e998e7c63c66  iida-az2-p01-net01-net02-tcp               deny      tcp         jp-east-1b
bb2dc88c-1e67-4233-8df4-cb45eb8c5e6b  deny-all-icmp                              deny      icmp        jp-east-1b
c6c17dd7-d40f-4c03-9e66-c2829699a30a  iida-az2-p01-net02-any-icmp                allow     icmp        jp-east-1b
e3ba3294-e008-4476-ab9a-925670f9383b  iida-az2-p01-net02-any-tcp                 allow     tcp         jp-east-1b
fea40b70-40fa-4885-8325-a06651cd4ddb  iida-az2-p01-net02-any-udp                 allow     udp         jp-east-1b
07773c9a-6dd9-45f4-8722-ddfbf2981515  iida-az1-p01-net01-any-icmp                allow     icmp        jp-east-1a
114d70cc-3c3c-4e17-a85c-fa995a084f44  iida-az1-p01-net02-any-tcp                 allow     tcp         jp-east-1a
1583ce48-608c-429e-92cf-a82471929111  iida-az1-p01-net02-any-icmp                allow     icmp        jp-east-1a
1d048151-593e-4c16-87cc-ba37fb55a811  iida-az1-p01-net02-any-udp                 allow     udp         jp-east-1a
21fc602c-5aa1-4bdd-b145-7f4872e7e470  iida-az1-p01-net01-net02-icmp              deny      icmp        jp-east-1a
29ad528b-f868-49ee-bc84-6034f960dcba  iida-az1-p01-net01-any-udp                 allow     udp         jp-east-1a
3158c601-4ce7-40ef-9efa-cee09968951e  deny-all-icmp                              deny      icmp        jp-east-1a
79ca78c3-6905-4dde-9ff2-e26c1f9091e0  iida-az1-p01-net01-net02-udp               deny      udp         jp-east-1a
8bd856d6-1ee1-4402-a69b-65c3381d5c26  deny-all-tcp                               deny      tcp         jp-east-1a
a9e5141a-8b29-408c-98c6-c64efb2437de  iida-az1-p01-net01-any-tcp                 allow     tcp         jp-east-1a
ba6152b5-1d7c-44af-8425-e7439883523c  iida-az1-p01-fip-icmp                      deny      icmp        jp-east-1a
c5e92187-d9c8-4887-99d3-e096a0695f2a  iida-az1-p01-fip-icmp-global               deny      icmp        jp-east-1a
cf17f5bf-398e-4602-937d-a4da6b07a162  deny-all-udp                               deny      udp         jp-east-1a
f89e509f-9cea-4587-bba6-63163ab41c73  iida-az1-p01-net01-net02-tcp               deny      tcp         jp-east-1a
====================================  =============================  ==========  ========  ==========  ===================
```

たくさんありますが、親になっているポリシーを削除したので全てunusedになっています。
これらを一括で削除します。

```
bash-4.4$ ./bin/k5-list-fw-rules.py --unused | ./bin/k5-delete-fw-rule.py -
0d7d84d9-3b64-4d6e-8aa9-e2276073321b
status_code: 204

0f2a1d89-676f-4741-8bf3-5c8a72794212
status_code: 204

1cabdeee-6835-4727-940f-57eb0a3cef04
status_code: 204

28e4a83c-8580-466b-8ffa-3e67b7f5e520
status_code: 204

2ba9dca6-8e3f-4a2f-867a-71e7e6b74f2f
status_code: 204

66d1ab16-ec6c-40d4-8b2d-64a92319757c
status_code: 204

ab470fe0-d3e0-4f5f-8f28-eb6de66fd3e3
status_code: 204

b338b0b9-dc57-4d10-b5cf-e998e7c63c66
status_code: 204

bb2dc88c-1e67-4233-8df4-cb45eb8c5e6b
status_code: 204

c6c17dd7-d40f-4c03-9e66-c2829699a30a
status_code: 204

e3ba3294-e008-4476-ab9a-925670f9383b
status_code: 204

fea40b70-40fa-4885-8325-a06651cd4ddb
status_code: 204

07773c9a-6dd9-45f4-8722-ddfbf2981515
status_code: 204

114d70cc-3c3c-4e17-a85c-fa995a084f44
status_code: 204

1583ce48-608c-429e-92cf-a82471929111
status_code: 204

1d048151-593e-4c16-87cc-ba37fb55a811
status_code: 204

21fc602c-5aa1-4bdd-b145-7f4872e7e470
status_code: 204

29ad528b-f868-49ee-bc84-6034f960dcba
status_code: 204

3158c601-4ce7-40ef-9efa-cee09968951e
status_code: 204

79ca78c3-6905-4dde-9ff2-e26c1f9091e0
status_code: 204

8bd856d6-1ee1-4402-a69b-65c3381d5c26
status_code: 204

a9e5141a-8b29-408c-98c6-c64efb2437de
status_code: 204

ba6152b5-1d7c-44af-8425-e7439883523c
status_code: 204

c5e92187-d9c8-4887-99d3-e096a0695f2a
status_code: 204

cf17f5bf-398e-4602-937d-a4da6b07a162
status_code: 204

f89e509f-9cea-4587-bba6-63163ab41c73
status_code: 204

bash-4.4$
```

<BR>

## ルータの削除

経路情報や繋がっているポート、外部ネットワークを外していかないといけないので、ルータの削除が一番めんどくさいです。
FAQにも書かれているくらいです。

[仮想ルータを削除できません。](https://k5-doc.jp-east-1.paas.cloud.global.fujitsu.com/doc/jp/iaas/faqlist_iaas.html#faq_iaas_00009 "IaaS FAQ")

> 以下の4点について確認いただいたうえで、事象が改善されない場合はお問い合わせ窓口までご連絡ください。
> - 仮想ルータにアタッチしている外部ネットワークをデタッチする。
> - 仮想ルータにアタッチしているポートをデタッチする。
> - ファイアーウォールが存在する場合は、ファイアーウォールを削除する。
> - 仮想ルータ配下のサブネットにグローバルIPアドレスが付与された仮想サーバが存在する場合は、グローバルIPアドレスを開放する。

ルータ一覧を表示します。

```
bash-4.4$ ./bin/k5-list-routers.py
GET /v2.0/routers
====================================  =================  ================================  ===================  ========
id                                    name               tenant_id                         availability_zone    status
====================================  =================  ================================  ===================  ========
ffbd70be-24cf-4dff-a4f6-661bf892e313  iida-az1-router01  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a           ACTIVE
c97f9aa5-eacc-48ae-b5df-82784bce8b63  iida-az2-router01  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b           ACTIVE
====================================  =================  ================================  ===================  ========
bash-4.4$
```

ルータの詳細を表示します。

```
bash-4.4$ ./bin/k5-list-routers.py | ./bin/k5-show-router.py -
router_id: ffbd70be-24cf-4dff-a4f6-661bf892e313
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

router_id: c97f9aa5-eacc-48ae-b5df-82784bce8b63
GET /v2.0/routers/{router_id}
==============  ====================================
name            iida-az2-router01
id              c97f9aa5-eacc-48ae-b5df-82784bce8b63
az              jp-east-1b
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================

external_gateway_info
===========  ====================================
enable_snat  True
network_id   4516097a-84dd-476f-824a-6b2fd3cc6499
===========  ====================================

'routes' is not set.

bash-4.4$
```

external_gateway_infoを持っていたらそれを外します。
--network-idに""を指定してアップデートすると外れます。

```
bash-4.4$ ./bin/k5-update-router.py \
--router-id  c97f9aa5-eacc-48ae-b5df-82784bce8b63 \
--network-id ""

set external_gateway_info to null
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az2-router01
id              c97f9aa5-eacc-48ae-b5df-82784bce8b63
az              jp-east-1b
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
```

経路情報を削除します。
これをやらないとポートの削除ができません。

- extra-routes.yaml

を編集します。

```
#
# iida-az1-router01
#
ffbd70be-24cf-4dff-a4f6-661bf892e313:

  # 経路情報
  routes:

```

このファイルを使って経路情報をアップデートします。

```
bash-4.4$ ./bin/k5-update-extra-routes.py ffbd70be-24cf-4dff-a4f6-661bf892e313
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================

'external_gateway_info' is not set.

'routes' is not set.
bash-4.4$
```

ルータからポートを外します。
これをやらないとルータを削除できないのですが、これが実にめんどくさい！

ルータにどのポートがつながっているか調べないといけません。
名前で推測しましょう。

> NOTE:
>
> ポートに名前を付けてなかったらそれこそ面倒です。オーナーのIDとルータIDが一致するものを探さないといけません。

ルータ１のポートひとつめ。

```
bash-4.4$ ./bin/k5-disconnect-router.py \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--port-id 689d24c7-02a2-4dfd-b809-9ad4060e079f

status_code: 200
PUT /v2.0/routers/{router_id}/add_router_interface
=========  ====================================
id         ffbd70be-24cf-4dff-a4f6-661bf892e313
port_id    689d24c7-02a2-4dfd-b809-9ad4060e079f
subnet_id  abbbbcf4-ea8f-4218-bbe7-669231eeba30
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
=========  ====================================
```

ルータ１のポートふたつめ。

```
bash-4.4$ ./bin/k5-disconnect-router.py \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--port-id bdab1ca6-fd32-4729-9e97-3827b72d7bc5

status_code: 200
PUT /v2.0/routers/{router_id}/add_router_interface
=========  ====================================
id         ffbd70be-24cf-4dff-a4f6-661bf892e313
port_id    bdab1ca6-fd32-4729-9e97-3827b72d7bc5
subnet_id  2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
=========  ====================================
```

ルータ２のポートひとつめ。

```
bash-4.4$ ./bin/k5-disconnect-router.py \
--router-id c97f9aa5-eacc-48ae-b5df-82784bce8b63 \
--port-id 59114983-8715-4dc7-879d-afbf69ef19a7

status_code: 200
PUT /v2.0/routers/{router_id}/add_router_interface
=========  ====================================
id         c97f9aa5-eacc-48ae-b5df-82784bce8b63
port_id    59114983-8715-4dc7-879d-afbf69ef19a7
subnet_id  07041634-9f01-4518-a2c8-1e6ea8d956ee
az         jp-east-1b
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
=========  ====================================
bash-4.4$
```

ルータ２のポートふたつめ。

```
bash-4.4$ ./bin/k5-disconnect-router.py \
--router-id c97f9aa5-eacc-48ae-b5df-82784bce8b63 \
--port-id c0b78abd-39fb-4833-97b0-8050d93b9cd5

status_code: 200
PUT /v2.0/routers/{router_id}/add_router_interface
=========  ====================================
id         c97f9aa5-eacc-48ae-b5df-82784bce8b63
port_id    c0b78abd-39fb-4833-97b0-8050d93b9cd5
subnet_id  50bf50fa-816b-4e7e-98da-8379d9675101
az         jp-east-1b
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
=========  ====================================
bash-4.4$
```

ここまでキレイにしたらルータそのものを削除します。

```
bash-4.4$ ./bin/k5-list-routers.py | ./bin/k5-delete-router.py -
status_code: 204

status_code: 204

```

<BR>

## コネクタエンドポイントの削除

コネクタエンドポイントの情報を表示します。

```
bash-4.4$ ./bin/k5-list-network-connector-endpoints.py | ./bin/k5-show-network-connector-endpoint.py -
ncep_id: 848a40c2-7ded-4df8-a43d-e55b912811a2
GET /v2.0/network_connector_endpoints/{network connector endpoint id}
====================  ====================================
name                  iida-az1-ncep
id                    848a40c2-7ded-4df8-a43d-e55b912811a2
endpoint_type         availability_zone
network_connector_id  88f343e8-a956-4bcc-853f-3c40d53cbb49
tenant_id             a5001a8b9c4a4712985c11377bd6d4fe
location              jp-east-1a
====================  ====================================
```

コネクタエンドポイントにつながっているポートを削除します。

これも面倒です。
どのポートがコネクタエンドポイントにつながっているのか調べないといけません。
ポートの名前で推測しましょう。

```
bash-4.4$ ./bin/k5-list-ports.py
GET /v2.0/ports
====================================  =====================  ====================================  ========================  ===================
id                                    name                   network_id                            device_owner              availability_zone
====================================  =====================  ====================================  ========================  ===================
74233502-90d1-47f7-976e-f3def361d2a1  iida-az1-net02-port02  e3c166c0-7e90-4c6e-857e-87fd985f98ac  network:router_interface  jp-east-1a
====================================  =====================  ====================================  ========================  ===================
bash-4.4$
```

ポートを外します。

```
bash-4.4$ ./bin/k5-disconnect-network-connector-endpoint.py \
--ncep-id 848a40c2-7ded-4df8-a43d-e55b912811a2 \
--port-id 74233502-90d1-47f7-976e-f3def361d2a1

status_code: 200
{'interface': {'port_id': '74233502-90d1-47f7-976e-f3def361d2a1'}}
bash-4.4$
```

コネクタエンドポイントを削除します。

```
bash-4.4$ ./bin/k5-list-network-connector-endpoints.py | ./bin/k5-delete-network-connector-endpoint.py -
status_code: 204
```

<BR>

## ポートの削除

ルータからポートを外す、コネクタエンドポイントからポートを外す、という作業をするとポートそのものも削除されます。
したがってここまでの操作でだいたいは消えているはずです。

```
bash-4.4$ ./bin/k5-list-ports.py
GET /v2.0/ports
====  ======  ============  ==============  ===================
id    name    network_id    device_owner    availability_zone
====  ======  ============  ==============  ===================
====  ======  ============  ==============  ===================
bash-4.4$
```

もし存在したら一括で削除します。

```
bash-4.4$ ./bin/k5-list-ports.py | ./bin/k5-delete-port.py -
```

<BR>

## ネットワークコネクタの削除

ネットワークコネクタの一覧を表示します。

```
bash-4.4$ ./bin/k5-list-network-connectors.py
GET /v2.0/network_connectors
====================================  ===========  ====================================
id                                    name         network_connector_pool_id
====================================  ===========  ====================================
88f343e8-a956-4bcc-853f-3c40d53cbb49  iida-az1-nc  e0a80446-203e-4b28-abec-d4b031d5b63e
====================================  ===========  ====================================
```

一括で削除します。

```
bash-4.4$ ./bin/k5-list-network-connectors.py | ./bin/k5-delete-network-connector.py -
status_code: 204
```

<BR>

## ネットワークの削除

ネットワークの一覧を表示します。
外部ネットワークを除外するためにgrep -v inf_をパイプしています。

```
bash-4.4$ ./bin/k5-list-networks.py | grep -v inf_
GET /v2.0/networks
====================================  =================  ================================  ===================  ========
id                                    name               tenant_id                         availability_zone    status
====================================  =================  ================================  ===================  ========
8f15da62-c7e5-47ec-8668-ee502f6d00d2  iida-az1-net01     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a           ACTIVE
e3c166c0-7e90-4c6e-857e-87fd985f98ac  iida-az1-net02     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a           ACTIVE
0cbf1e4d-479b-4336-8ba9-eb530fe55adb  iida-az2-net01     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b           ACTIVE
8b004a16-c5a2-4e1d-ab9e-a417fef45ec7  iida-az2-net02     a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1b           ACTIVE
====================================  =================  ================================  ===================  ========
```

ネットワークの子供にはサブネットがいますが、気にせず削除します。
ネットワークを消すとサブネットも同時に消えてくれます。

```
bash-4.4$ ./bin/k5-list-networks.py | grep -v inf_ | ./bin/k5-delete-network.py -
status_code: 204

status_code: 204

status_code: 204

status_code: 204

bash-4.4$
```

以上でK5内のネットワーク環境は全てなくなりました。
