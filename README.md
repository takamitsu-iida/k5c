# k5c

K5のネットワーク環境を操作するためのPythonスクリプト集です。

通常はマニュアル通りcurlコマンドを使えばいいと思います。

パラメータシートを読み取ってコマンド一発でネットワークを構成したり、稼働している環境からパラメータシートを起こしたりするなら、Pythonスクリプトを駆使するといいと思います。

<br>
<br>

# K5ネットワークの基礎知識

## ネットワークとサブネットとポートの関係

ネットワークとサブネット、ポートの関係はこのようになっています。

```
Availability Zone
│
│
└─ネットワーク(network_id)
　　│　
　　│
　　├─サブネット(subnet_id)
　　│　　ネットワークとサブネットは1:1の関係
　　│　　DHCP関連の設定(DNSサーバ、追加経路など)はここ
　　│
　　├─ポート(port_id)
　　│　│　固定IPアドレス(fixed_ips)
　　│　│
　　│　└─デバイスオーナ(仮想サーバや仮想ルータ、コネクタエンドポイント)
　　│
　　└─ポート(port_id)
　　　　│　固定IPアドレス(fixed_ips)
　　　　│
　　　　└─デバイスオーナ(仮想サーバや仮想ルータ、コネクタエンドポイント)
```

ネットワークはサブネットやポートを紐付けるための器になります。それ自身に設定される情報は多くはありません。

ネットワークとサブネットは1:1の関係になり、器となるネットワークを作成した後、そのIDを指定してサブネットを作成します。
OpenStackのネットワークは基本的にDHCPありきで動作します。仮想サーバに固定IPを割り当てる場合でも、アドレスの配布自体はDHCPで行います。DHCPに関連した情報もサブネットの中に設定します。DNSサーバの情報や、仮想サーバに追加のルーティング情報を配布したい場合も、サブネットの中に設定します。

ポートはNICと同じ役割をもちます。
ポートを作成するときに、ネットワークのIDを指定することで、どのネットワークにアタッチするか指定します。
IPアドレスはポートに対して付与されますので、サブネットのIDを指定する必要があります。
ポート作成後にオーナー（仮想サーバや仮想ルータ）との紐付けを行います。

以上の関係性から、作成すべき順番はこのようになります。

1. ネットワークを作成して、ネットワークIDを調べる
2. そのネットワークIDを指定してサブネットを作成する
3. ネットワークIDとサブネットIDを指定してポートを作成する
4. デバイス(仮想サーバや仮想ルータ)とポートを紐付ける


## ネットワークコネクタ

少々ややこしいのは、データセンター構内で別の物理ネットワークと接続する場合です。ネットワークコネクタという聞きなれない用語が登場します。

```
Availability Zone
│
│
└─ネットワークコネクタプール(network_connector_pool_id)
　　│　自分で作成することはできません
　　│
　　└─ネットワークコネクタ(network_connector_id)
　　　　│　外部向けの設定は事業者が実施
　　　　│
　　　　├─ネットワークコネクタエンドポイント(network_connector_endpoint_id)
　　　　│　│
　　　　│　└─ポート(port_id)
　　　　│
　　　　│
　　　　└─ネットワークコネクタエンドポイント(network_connector_endpoint_id)
　　　　　　│
　　　　　　└─ポート(port_id)
```

Availability Zoneの中にはネットワークコネクタプールというものが存在します。これは最初から存在するもので、削除も追加もできません。

ネットワークコネクタプールの中にネットワークコネクタを作成します。これが外部との接点になります。外側の接続設定はK5事業者が行いますので、（申請書を書くとか）何らかの形で依頼をすることになると思います。

> NOTE:
>
> 2017年5月時点、ネットワークコネクタの作成はAPIを操作しなければいけません。

ネットワークコネクタには、コネクタエンドポイントを作成します。これが内側との接点になります。ポートのオーナーとしてコネクタエンドポイントを指定することで、内側のネットワークと紐付けられます。

ネットワークコネクタには複数のコネクタエンドポイントを作成できます。したがって、一つの構内接続を複数のプロジェクトで共有することもできます。

外部との接続を作成する順番としては、このようになります。

1. ネットワークコネクタプールのIDを調べる
2. そのプールのIDを指定して、ネットワークコネクタを作成する
3. 作成したネットワークコネクタのIDを調べる
4. そのネットワークコネクタのIDを指定してコネクタエンドポイントを作成する
5. 事前に作成しておいたポートのオーナーとしてコネクタエンドポイントを指定する

<BR>
<BR>

# ネットワークの構成イメージと作成手順概要

## 全体の構成イメージ

簡単な構成です。
インターネットからの接続を受けつつ、裏側ではイントラとも接続する構成です。

![fig010](https://cloud.githubusercontent.com/assets/21165341/25983547/6f9d7c5e-3720-11e7-9aa0-7fd6be8258ee.png)

## K5の構成に当てはめると

K5のコンポーネントで構成するとこのようになります。
ルータ、ポート、ネットワーク、サブネットはそれぞれ独立して作成して、あとから関連付ける、という操作になります。

裏側はネットワークコネクタとコネクタエンドポイントで接続します。

![fig020](https://cloud.githubusercontent.com/assets/21165341/25983573/9d325b80-3720-11e7-86fd-bbf558a9eb97.png
)

## 手順１．事業者側のIDを調べる

外部ネットワークとネットワークコネクタプールは事業者側で用意するもので、自分では作成できません。

最初にやることは、それらIDの調査です。
後々使いますので管理資料に記載しておきましょう。頻繁にコピーペーストすることになりますので、コピペしやすい文書が良いと思います。

- k5-list-networks.py
- k5-list-network-connector-pools.py

![fig030](https://cloud.githubusercontent.com/assets/21165341/25997591/959fe2ca-3757-11e7-9bba-c94e7d35952e.png)

```
bash-4.4$ ./k5-list-networks.py | grep inf_az1
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
```
外部ネットワークの名前とIDを表にするとこうなります。
どれを使ってもいいのですが、-net01や-net02あたりはグローバルアドレスの空きがなく、使えない可能性が高いです。

|name|network_id|
|:--|:--|
|inf_az1_ext-net01|af4198a9-b392-493d-80ec-a7c6e5a1c22a|
|inf_az1_ext-net02|92f386c1-59fe-48ca-8cf9-b95f81920466|
|inf_az1_ext-net03|6d9df982-7a89-462a-8b17-8a8e5befa63e|
|inf_az1_ext-net04|a4715541-c915-444b-bed6-99aa1e8b15c9|
|inf_az1_ext-net05|cd4057bd-f72e-4244-a7dd-1bcb2775dd67|


```
bash-4.4$ ./k5-list-network-connector-pools.py
GET /v2.0/network_connector_pools
====================================  ============================
id                                    name
====================================  ============================
e0a80446-203e-4b28-abec-d4b031d5b63e  jp-east-1a_connector_pool_01
====================================  ============================
```
ネットワークコネクタプールの名前とIDを表にするとこうなります。

|name|network_connector_pool_id|
|:--|:--|
|jp-east-1a_connector_pool_01|e0a80446-203e-4b28-abec-d4b031d5b63e|

<BR>

## 手順２．ルータを作成する

名前を決めてルータを作成します。作成したらIDをメモしておきます。

- k5-create-router.py

![fig040](https://cloud.githubusercontent.com/assets/21165341/25983622/e8ecfc38-3720-11e7-8349-c07a878317dd.png)

```
bash-4.4$ ./k5-create-router.py --name iida-az1-router01
POST /v2.0/routers
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
bash-4.4$
```

|name|router_id|
|:--|:--|
|iida-az1-router01|ffbd70be-24cf-4dff-a4f6-661bf892e313|

<BR>

## 手順３．ネットワークを作成する

名前を決めてネットワークを作成します。作成したらIDをメモしておきます。

- k5-create-router.py

![fig050](https://cloud.githubusercontent.com/assets/21165341/25983724/824dc0c4-3721-11e7-990f-55360455cfa3.png)

```
bash-4.4$ ./k5-create-network.py --name iida-az1-net01
POST /v2.0/networks
=========  ====================================
name       iida-az1-net01
id         8f15da62-c7e5-47ec-8668-ee502f6d00d2
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================

bash-4.4$ ./k5-create-network.py --name iida-az1-net02
POST /v2.0/networks
=========  ====================================
name       iida-az1-net02
id         e3c166c0-7e90-4c6e-857e-87fd985f98ac
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
bash-4.4$
```

|name|network_id|
|:--|:--|
|iida-az1-net01|8f15da62-c7e5-47ec-8668-ee502f6d00d2|
|iida-az1-net02|e3c166c0-7e90-4c6e-857e-87fd985f98ac|

<BR>

## 手順４．サブネットを作成する

ネットワークとサブネットは1:1の関係です。親になるネットワークのIDを指定してサブネットを作成します。このときに指定するパラメータは多数ありますが、最低限アドレス情報は必須です。作成時に指定しなかったパラメータは後からupdateできます。

- k5-create-subnet.py

![fig060](https://cloud.githubusercontent.com/assets/21165341/25983760/a816664e-3721-11e7-80ca-f75f4284733e.png)

```
bash-4.4$ ./k5-create-subnet.py --name iida-az1-subnet01 --network_id 8f15da62-c7e5-47ec-8668-ee502f6d00d2 --cidr 10.1.1.0/24
POST /v2.0/subnets
===========  ====================================
name         iida-az1-subnet01
id           abbbbcf4-ea8f-4218-bbe7-669231eeba30
az           jp-east-1a
cidr         10.1.1.0/24
gateway_ip   10.1.1.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   8f15da62-c7e5-47ec-8668-ee502f6d00d2
enable_dhcp  True
===========  ====================================

bash-4.4$ ./k5-create-subnet.py --name iida-az1-subnet02 --network_id e3c166c0-7e90-4c6e-857e-87fd985f98ac --cidr 10.1.2.0/24
POST /v2.0/subnets
===========  ====================================
name         iida-az1-subnet02
id           2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
az           jp-east-1a
cidr         10.1.2.0/24
gateway_ip   10.1.2.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   e3c166c0-7e90-4c6e-857e-87fd985f98ac
enable_dhcp  True
===========  ====================================
bash-4.4$
```

|name|subnet_id|cidr|
|:--|:--|:--|
|iida-az1-subnet01|abbbbcf4-ea8f-4218-bbe7-669231eeba30|10.1.1.0/24|
|iida-az1-subnet02|2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6|10.1.2.0/24|

<BR>

## 手順５．ポートを作成する

どのネットワークに接続するかを指定してポートを作成します。
IPアドレスを指定することもできます。
指定しなければ自動採番されます。

> ルータ用のポートであれば、IPアドレスの第四オクテットを.1にするとよいと思います。指定しないと.2以降が採番されます。

- k5-create-port.py

![fig070](https://cloud.githubusercontent.com/assets/21165341/25983776/bfdc2b7e-3721-11e7-899b-75a370cdc1a5.png)

```
bash-4.4$ ./k5-create-port.py --name iida-az1-net01-port01 --network_id 8f15da62-c7e5-47ec-8668-ee502f6d00d2 --subnet_id abbbbcf4-ea8f-4218-bbe7-669231eeba30 --ip_address 10.1.1.1
POST /v2.0/ports
=================  ====================================
name               iida-az1-net01-port01
id                 430497b1-fdd4-4857-bc43-53286b5a27f5
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         8f15da62-c7e5-47ec-8668-ee502f6d00d2
binding:vnic_type  normal
mac_address        fa:16:3e:82:3c:16
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.1.1      abbbbcf4-ea8f-4218-bbe7-669231eeba30
============  ====================================
bash-4.4$

bash-4.4$ ./k5-create-port.py --name iida-az1-net02-port01 --network_id e3c166c0-7e90-4c6e-857e-87fd985f98ac --subnet_id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6 --ip_address 1
0.1.2.1
POST /v2.0/ports
=================  ====================================
name               iida-az1-net02-port01
id                 bdab1ca6-fd32-4729-9e97-3827b72d7bc5
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
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

bash-4.4$ ./k5-create-port.py --name iida-az1-net02-port02 --network_id e3c166c0-7e90-4c6e-857e-87fd985f98ac --subnet_id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6 --ip_address 1
0.1.2.9
POST /v2.0/ports
=================  ====================================
name               iida-az1-net02-port02
id                 6c73b1a0-ab3d-46e5-9515-f04e9f660423
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         e3c166c0-7e90-4c6e-857e-87fd985f98ac
binding:vnic_type  normal
mac_address        fa:16:3e:71:8f:fa
=================  ====================================

============  ====================================
ip_address    subnet_id
============  ====================================
10.1.2.9      2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
============  ====================================
bash-4.4$
```

|name|port_id|address|
|:--|:--|:--|
|iida-az1-net01-port01|430497b1-fdd4-4857-bc43-53286b5a27f5|10.1.1.1|
|iida-az1-net02-port01|bdab1ca6-fd32-4729-9e97-3827b72d7bc5|10.1.2.1|
|iida-az1-net02-port02|6c73b1a0-ab3d-46e5-9515-f04e9f660423|10.1.2.9|

<BR>

## 手順６．ルータとポートを接続する

作成済みのポートIDを指定してルータの情報を更新します。

- k5-connect-router.py

![fig080](https://cloud.githubusercontent.com/assets/21165341/25983791/d2e6ce54-3721-11e7-9b52-8a71bd9a3804.png)

```
bash-4.4$ ./k5-connect-router.py --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --port_id 430497b1-fdd4-4857-bc43-53286b5a27f5
status_code: 200

bash-4.4$ ./k5-connect-router.py --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --port_id bdab1ca6-fd32-4729-9e97-3827b72d7bc5
status_code: 200
```

<BR>

## 手順７．ネットワークコネクタを作成する

事業者が用意するネットワークコネクタプールを指定して、ネットワークコネクタを作成します。

- k5-create-network-connector.py

ネットワークコネクタが外部の物理ネットワークとの境界になると考えられます。ネットワークコネクタに設定すべきパラメータは、申請書にもとづいて変更をかけていきます。

![fig090](https://cloud.githubusercontent.com/assets/21165341/25983801/e2b0d442-3721-11e7-8e6d-1a02097d6681.png)

```
bash-4.4$ ./k5-create-network-connector.py --name iida-az1-nc --nc_pool_id e0a80446-203e-4b28-abec-d4b031d5b63e
POST /v2.0/network_connectors
=======  ====================================
name     iida-az1-nc
id       88f343e8-a956-4bcc-853f-3c40d53cbb49
pool_id  e0a80446-203e-4b28-abec-d4b031d5b63e
=======  ====================================
bash-4.4$
```

|name|network_connector_id|
|:--|:--|
|iida-az1-nc|88f343e8-a956-4bcc-853f-3c40d53cbb49|

<BR>

## 手順８．コネクタエンドポイントを作成する

ネットワークコネクタを指定してコネクタエンドポイントを作成します。
コネクタエンドポイントは論理ルータと同じイメージです。

- k5-create-network-connector-endpoint.py

![fig100](https://cloud.githubusercontent.com/assets/21165341/25998521/53b33d3a-375c-11e7-867f-46455985863e.png)

```
bash-4.4$ ./k5-create-network-connector-endpoint.py --name iida-az1-ncep --nc_id 88f343e8-a956-4bcc-853f-3c40d53cbb49
POST /v2.0/network_connector_endpoints
=============  ====================================
name           iida-az1-ncep
id             848a40c2-7ded-4df8-a43d-e55b912811a2
nc_id          88f343e8-a956-4bcc-853f-3c40d53cbb49
tenant_id      a5001a8b9c4a4712985c11377bd6d4fe
location       jp-east-1a
endpoint_type  availability_zone
=============  ====================================
bash-4.4$
```

|name|network_connector_endpoint_id|
|:--|:--|
|iida-az1-ncep|848a40c2-7ded-4df8-a43d-e55b912811a2|

<BR>

## 手順９．コネクタエンドポイントとポートを接続する

作成済みのポートとコネクタエンドポイントを接続します。

- k5-connect-network-connector-endpoint.py

![fig110](https://cloud.githubusercontent.com/assets/21165341/25983816/088d49a2-3722-11e7-8f13-07ee1347f6e5.png)

```
bash-4.4$ ./k5-connect-network-connector-endpoint.py --ncep_id 848a40c2-7ded-4df8-a43d-e55b912811a2 --port_id 6c73b1a0-ab3d-46e5-9515-f04e9f660423
status_code: 200
{'interface': {'port_id': '6c73b1a0-ab3d-46e5-9515-f04e9f660423'}}
```

<BR>

## 手順１０．ルータと外部ネットを接続する

ルータと外部ネットワークを接続します。
外部ネットワークの場合にはポートを経由しません。直接ネットワークを指定します。

- k5-update-router.py

![fig120](https://cloud.githubusercontent.com/assets/21165341/25983834/255b78e2-3722-11e7-801e-11882cc3e436.png)

```
bash-4.4$ ./k5-update-router.py --router_id ffbd70be-24cf-4dff-a4f6-661bf892e313 --network_id cd4057bd-f72e-4244-a7dd-1bcb2775dd67
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
```

ここではinf_az1_ext-net05を使っています。

<BR>
<BR>

# ルーティングの設定と手順概要

> NOTE:
>
> 公開されているドキュメントを読んでもよくわからない部分があります。ここに記載していることは個人的な理解です。

## 手順１１．サブネットのルーティング設定(DHCP設定)

同じネットワーク（サブネット）にルータが2台いる場合、どの宛先はどっち、という判断が必要です。VMのルーティングテーブルを手動で変更してもいいのかもしれませんが、OpenStackではDHCPのオプションコード121（RFC3442 : Classless Static Route Option for DHCPv4）を使ってVMに経路情報を伝えます。経路を追加、削除した場合はVMを再起動してDHCPで取り直さないと反映されません。

ここまでの例では、

- iida-az1-net01(10.1.1.0/24)はルータ1台のセグメントなので、ルーティングの設定は不要（デフォルトルートに従う）
- iida-az1-net02(10.1.2.0/24)はルータとコネクタエンドポイントがいるので、どっちの出口を使うか、ルーティングの設定が必要

ということになります。

![fig130](https://cloud.githubusercontent.com/assets/21165341/26041996/6e929a94-396c-11e7-84d6-2b6a1cad1345.png)

iida-az1-net02からみたとき、-net01(10.1.1.0/24)はルータ向け、その他の10系のアドレス(10.0.0.0/8)はネットワークコネクタ向け、インターネットはルータ向け、となります。

- k5-update-subnet.py
- k5-update-subnet.yaml

このスクリプトは設定パラメータが多いだけでなく、形式が複雑なので、YAML形式の設定ファイルを作って読み込ませます。

```yaml
# 第一階層のキーは対象サブネットのIDにしてください

#
# iida-az1-subnet02
#
2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6:
  # サブネットの名前
  # name: iida-az1-subnet02

  # そのサブネットにおけるデフォルトゲートウェイのIPアドレス
  # gateway_ip: 10.1.2.1

  # DNSサーバ
  # AZ1の場合は 133.162.193.9 133.162.193.10
  # AZ2の場合は 133.162.201.9 133.162.201.10
  # その他は 8.8.8.7 8.8.8.8
  dns_nameservers:
    - 133.162.193.9
    - 133.162.193.10

  # ホストルート
  host_routes:
    - destination: 10.1.1.0/24
      nexthop: 10.1.2.1
    - destination: 10.0.0.0/8
      nexthop: 10.1.2.9
    - destination: 172.16.0.0/12
      nexthop: 10.1.2.9
    - destination: 192.168.0.0/16
      nexthop: 10.1.2.9
```

実行結果。

```
bash-4.4$ ./k5-update-subnet.py --subnet_id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
PUT /v2.0/subnets/{subnet_id}
===========  ====================================
name         iida-az1-subnet02
id           2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
az           jp-east-1a
cidr         10.1.2.0/24
gateway_ip   10.1.2.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   e3c166c0-7e90-4c6e-857e-87fd985f98ac
enable_dhcp  True
===========  ====================================


=================
dns_nameservers
=================
133.162.193.9
133.162.193.10
=================


==============  =========
destination     nexthop
==============  =========
172.16.0.0/12   10.1.2.9
192.168.0.0/16  10.1.2.9
10.1.1.0/24     10.1.2.1
10.0.0.0/8      10.1.2.9
==============  =========
```

<BR>

## 手順１２．ルータのルーティング設定

ルータはスタティックルーティングで動作します。

サブネットに設定したhost_routes経路をルータが自動で拾ってくれるのか、は疑問です。
サブネットのhost_routes経路はあくまでDHCPサーバの設定パラメータなので、ルータには反映されないと思ったほうがいいでしょう。

![fig140](https://cloud.githubusercontent.com/assets/21165341/26043631/9f409184-3979-11e7-8809-63344e979993.png)

ルータから見た時、-net01(10.1.1.0/24)と-net02(10.1.2.0/24)は自足に接続していますので、Locally connected経路です。
これらについては設定不要です。
また、外部ネットワークとの接続を持っていますので、デフォルトルートも自動的にそちらを向きます。

ネットワークコネクタを経由しないと通信できない通信はスタティックで追加設定します。
イントラネット向けの通信なので、プライベートIPアドレスを集約して、ネットワークコネクタに向けておくのが無難でしょう。

> 複数のルータを使う構成では、どの宛先はどのゲートウェイを使うか、という洗い出しを、全てのルータについて行わなければいけません。
>
> スタティックルーティングはたいへん面倒です。

- k5-update-extra-routes.py
- k5-update-extra-routes.yaml

このスクリプトはYAML形式の設定ファイルを作って読み込ませます。
ルータごとにYAMLファイルを作成しておくとよいでしょう。

```yaml
# 第一階層のキーは対象ルータのIDにしてください

#
# iida-az1-router01
#
ffbd70be-24cf-4dff-a4f6-661bf892e313:

  # 経路情報
  routes:
    - destination: 10.0.0.0/8
      nexthop: 10.1.2.9
    - destination: 172.16.0.0/12
      nexthop: 10.1.2.9
    - destination: 192.168.0.0/16
      nexthop: 10.1.2.9
```

実行結果。

```
bash-4.4$ ./k5-update-extra-routes.py --filename r1.yaml ffbd70be-24cf-4dff-a4f6-661bf892e313
PUT /v2.0/routers/{router_id}
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
```

<BR>

## 手順１３．ネットワークコネクタへのルーティング設定

K5と構内で接続するルータを用意して、eBGPピアを張ります。
申請書にもとづいて手続きを進める必要があります。


### コネクタエンドポイント自身のルーティング

コネクタエンドポイントはルータみたいなものですが、ルーティングを操作するためのAPIは公開されていません。
したがって、事業者に申請して設定を入れてもらうことになります。

ここでの例では、K5の中にある経路のうち、
-net02(10.1.2.0/24)はネットワークコネクタに接続した自足経路です。この経路については、接続しているポートのIDを事業者に伝えればいいでしょう。ポートさえ分かれば、それがどのネットワークに接続していて、そのサブネットは何か、ということろまで追跡可能です。

-net01(10.1.1.0/24)はコネクタエンドポイントにスタティックルーティングを追加しないと到達できない経路です。
アドレスとゲートウェイをセットにして事業者に伝えればいいでしょう。
（申請しないと、事業者は知り得ない情報です）

したがって、事業者への申請書には最低限、以下の情報が必要になると思われます。

- 作成したネットワークコネクタのID(物理接続の対象を識別)
- コネクタエンドポイントが接続しているポートのID(自足経路を知るために必要)
- コネクタエンドポイントに追加するスタティックルーティングの一覧情報(この例では、-net01の10.1.1.0/24とゲートウェイ)


### K5→外部方向に送信する経路の設定

K5の中で使っている経路をeBGPで外部に広告します。

コネクタエンドポイントが持っている経路情報（自足経路とスタティック経路）がeBGPで外部にでてくると思えばいいでしょう。
申請書を正しく書くだけです。


### 外部方向→K5に送信する経路の設定

逆に外部ネットワークで使っている経路情報をeBGPでK5側に伝えるには、準備した接続ルータでeBGPの設定を行います。

eBGPでK5側に伝えられる経路の数には制限があり、上限200経路とされています。
うまく集約をかけて不要な経路を流さないように工夫が必要です。
内部で使っているOSPF経路を全てeBGPに変換して伝える、といったことをやると、上限200経路に抵触するリスクが生じます。

だいたいの場合はプライベートIPアドレスを集約して伝えれば問題ないでしょう。


<BR>
<BR>

# スクリプトについて

## Pythonのバージョンと依存モジュール

Pythonはversion 3を想定しています。

以下のモジュールを利用しています。
lib/site-packagesにこれらを含めていますので、インストールは不要です。

 - requests
 - tabulate
 - pyyaml
 - openpyxl (トライ中)

## 事前に必要な情報

- K5管理者のユーザ名
- K5管理者のパスワード
- ドメイン名(契約番号と同じ)
- プロジェクトID(32桁英数字)
- グループ内のドメインID(32桁英数字)
- リージョン名(例：jp-east-1)

この他、必要に応じてプロキシサーバの情報が必要です。


## スクリプトの設定

lib/k5c/_k5config.py のファイル名をk5config.pyに変更して、上記の情報で書き換えてください。

k5config.py

```python
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
```

## スクリプトの実行

scriptsフォルダに実行用のスクリプトを置いています。

Windowsのコマンドプロンプトでも実行できますが、画面の横幅が狭いため見苦しい表示になってしまいます。
TeraTERMでCygwinに接続する、出力をファイルにリダイレクトしてエディタで確認する、といった工夫をするといいと思います。

### k5-token.py

APIエンドポイントに接続できるかテストするためのスクリプトで、通常は使いません。
これがエラーを返すようなら、k5config.pyが存在しないか、k5config.pyの設定パラメータに誤りがあります。

```
bash-4.4$ ./k5-token.py
{
  "expires_at": "2017-05-02T13:31:28.092961Z",
  "X-Subject-Token": "f240eccd302f4a31b3ccdb4b0d1bcd7f",
  "issued_at": "2017-05-02T10:31:28.092987Z"
}
```

時刻はISO 8601形式のUTCになっています。
issued_atとexpires_atの差分が3時間ほどありますので、トークンの有効期間は3時間と考えられます。
トークンは取得するたびに変わります。
払い出せるトークンの数には制限があるかもしれませんので、
一度取得したトークンはキャッシュして使いまわすようにしています。


### k5-list-xxx.py

一覧表示します。

### k5-create-xxx.py

作成します。

### k5-delete-xxx.py

削除します。

### k5-show-xxx.py

詳細表示します。

### k5-update-router.py

外部ネットワークと接続します。

### k5-connect-router.py

ルータとポートを接続します。

### k5-disconnect-router.py

ルータとポートを切り離します。

> 実行すると、なぜかポート自体が削除されます。作り直してください。

### k5-connect-network-connector-endpoint.py

コネクターエンドポイントを内部ネットワークに接続します。

### k5-disconnect-network-connector-endpoint.py

コネクターエンドポイントと内部ネットワークを切り離します。
