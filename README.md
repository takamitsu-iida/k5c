# k5c

Fujitsu K5のネットワーク環境を操作するためのPythonスクリプト集です。

> NOTE:
>
> K5を使える環境にいませんので、このレポジトリは凍結されています。

<br>
<br>

# K5ネットワークの基礎知識

K5のネットワークを構成する要素は、作成と同時に接続するものと、別々に作成して後からくっつけるものがありますので、構成要素の親子関係を理解することが大事です。

<BR>

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

ネットワークとサブネットは1:1の関係になり、器になるネットワークを作成した後、そのIDを指定してサブネットを作成します。したがって、サブネットは作成と同時に親子関係を作り、単独で存在することはありません。

OpenStackのネットワークは基本的にDHCPありきで動作します。仮想サーバに固定IPを割り当てる場合でも、アドレスの配布自体はDHCPで行います。DHCPに関連した情報もサブネットの中に設定します。DNSサーバの情報や、仮想サーバに追加のルーティング情報を配布したい場合も、サブネットの中に設定します。

ポートはNICと同じ役割をもちます。
ポートを作成するときに、ネットワークのIDを指定することで、どのネットワークにアタッチするか指定します。したがって片足は必ずネットワークに接続した状態で存在します。また、IPアドレスはポートに対して付与されますので、サブネットのIDも指定する必要があります。
ポート作成後にオーナー（仮想サーバや仮想ルータ）との接続を行います。

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

![fig010](https://cloud.githubusercontent.com/assets/21165341/26092739/95c933d4-3a4d-11e7-84f4-8a957f90f589.png)

## K5の構成に当てはめると

K5のコンポーネントで構成するとこのようになります（↓）。

K5のネットワークは外部ネットワーク、（内部）ネットワーク、サブネット、ルータ、ポートで構成されます。
裏側（イントラ）との接続はネットワークコネクタとコネクタエンドポイントで構成されます。

![fig020](https://cloud.githubusercontent.com/assets/21165341/26092779/ca76a3fa-3a4d-11e7-8e95-541d76447e17.png)

## 手順１．事業者側のIDを調べる

外部ネットワークとネットワークコネクタプールは事業者側で用意するものなので、自分では作成できません。

最初にやることは、それらIDの調査です。
後々使いますので管理資料に記載しておきましょう。
頻繁にコピーペーストすることになりますので、コピペしやすい文書が良いと思います。

- bin/k5-list-networks.py
- bin/k5-list-network-connector-pools.py

![fig030](https://cloud.githubusercontent.com/assets/21165341/26092939/842681c6-3a4e-11e7-806e-1cfd0c58a435.png)

```
bash-4.4$ ./bin/k5-list-networks.py | grep inf_az1
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
```

外部ネットワークの名前とIDを表にするとこうなります（↓）。
どれを使ってもいいのですが、-net01や-net02あたりはグローバルアドレスの空きがなく、使えない可能性が高いです。

|name|network_id|
|:--|:--|
|inf_az1_ext-net01|af4198a9-b392-493d-80ec-a7c6e5a1c22a|
|inf_az1_ext-net02|92f386c1-59fe-48ca-8cf9-b95f81920466|
|inf_az1_ext-net03|6d9df982-7a89-462a-8b17-8a8e5befa63e|
|inf_az1_ext-net04|a4715541-c915-444b-bed6-99aa1e8b15c9|
|inf_az1_ext-net05|cd4057bd-f72e-4244-a7dd-1bcb2775dd67|


```
bash-4.4$ ./bin/k5-list-network-connector-pools.py
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

- bin/k5-create-router.py

![fig040](https://cloud.githubusercontent.com/assets/21165341/26093822/62bac796-3a52-11e7-9ab7-997d51abeade.png)

実行例。

```
bash-4.4$ ./bin/k5-create-router.py --name iida-az1-router01
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

作成したルータの名前とID。

|name|router_id|
|:--|:--|
|iida-az1-router01|ffbd70be-24cf-4dff-a4f6-661bf892e313|

<BR>

## 手順３．ネットワークを作成する

名前を決めてネットワークを作成します。作成したらIDをメモしておきます。

- bin/k5-create-router.py

![fig050](https://cloud.githubusercontent.com/assets/21165341/26093866/90769908-3a52-11e7-8da6-f312f55d15a1.png)

ネットワーク作成、一つ目。

```
bash-4.4$ ./bin/k5-create-network.py --name iida-az1-net01
POST /v2.0/networks
=========  ====================================
name       iida-az1-net01
id         8f15da62-c7e5-47ec-8668-ee502f6d00d2
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
```

ネットワーク作成、二つ目。

```
bash-4.4$ ./bin/k5-create-network.py --name iida-az1-net02
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

作成したネットワークの名前とID。

|name|network_id|
|:--|:--|
|iida-az1-net01|8f15da62-c7e5-47ec-8668-ee502f6d00d2|
|iida-az1-net02|e3c166c0-7e90-4c6e-857e-87fd985f98ac|

<BR>

## 手順４．サブネットを作成する

ネットワークとサブネットは1:1の関係です。
親になるネットワークのIDを指定してサブネットを作成します。
したがってサブネットは単独では存在できず、必ずネットワークとひも付きになります。

サブネット作成時に指定するパラメータは多数ありますが、最低限アドレス情報は必須です。
作成時に指定しなかったパラメータは後からupdateできます。

- bin/k5-create-subnet.py

![fig060](https://cloud.githubusercontent.com/assets/21165341/26093933/cfd832b4-3a52-11e7-9bb5-93067030f54d.png)


サブネット作成、一つ目。

```
bash-4.4$ ./bin/k5-create-subnet.py \
--name iida-az1-subnet01 \
--network-id 8f15da62-c7e5-47ec-8668-ee502f6d00d2 \
--cidr 10.1.1.0/24

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
```

サブネット作成、二つ目。

```
bash-4.4$ ./bin/k5-create-subnet.py \
--name iida-az1-subnet02 \
--network-id e3c166c0-7e90-4c6e-857e-87fd985f98ac \
--cidr 10.1.2.0/24

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

作成したサブネットの名前とID。

|name|subnet_id|cidr|
|:--|:--|:--|
|iida-az1-subnet01|abbbbcf4-ea8f-4218-bbe7-669231eeba30|10.1.1.0/24|
|iida-az1-subnet02|2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6|10.1.2.0/24|

<BR>

## 手順５．ポートを作成する

どのネットワークに接続するかを指定してポートを作成します。
したがってポートは単独では存在できず、必ず片足をネットワークに接続した状態になります。
作成直後は所有者が決まっていない空きポートということになります。

作成時にはIPアドレスを指定することもできます。
指定しなければ自動採番されます。
ポートを作成した時点でIPアドレスが決まってしまいますので、
仮想マシンのOS設定でアドレスを変えることはできないことに留意が必要です。

> NOTE:
>
> ルータ用のポートであれば、IPアドレスの第四オクテットを.1にするとよいと思います。指定しないと.2以降が採番されます。

- bin/k5-create-port.py

![fig070](https://cloud.githubusercontent.com/assets/21165341/26094015/262df0d6-3a53-11e7-95a8-2fcd1222cde4.png)

ポート作成、一つ目。

```
bash-4.4$ ./bin/k5-create-port.py \
--name iida-az1-net01-port01 \
--network-id 8f15da62-c7e5-47ec-8668-ee502f6d00d2 \
--subnet-id abbbbcf4-ea8f-4218-bbe7-669231eeba30 \
--ip-address 10.1.1.1

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
```

ポート作成、二つ目。

```
bash-4.4$ ./bin/k5-create-port.py \
--name iida-az1-net02-port01 \
--network-id e3c166c0-7e90-4c6e-857e-87fd985f98ac \
--subnet-id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6 \
--ip-address 10.1.2.1

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
```

ポート作成、三つ目。

```
bash-4.4$ ./bin/k5-create-port.py \
--name iida-az1-net02-port02 \
--network-id e3c166c0-7e90-4c6e-857e-87fd985f98ac \
--subnet-id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6 \
--ip-address 10.1.2.9

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

作成したポートの名前とID。

|name|port_id|address|
|:--|:--|:--|
|iida-az1-net01-port01|430497b1-fdd4-4857-bc43-53286b5a27f5|10.1.1.1|
|iida-az1-net02-port01|bdab1ca6-fd32-4729-9e97-3827b72d7bc5|10.1.2.1|
|iida-az1-net02-port02|6c73b1a0-ab3d-46e5-9515-f04e9f660423|10.1.2.9|

<BR>

## 手順６．ルータとポートを接続する

作成済みのポートIDを指定してルータとポートを接続します。

- bin/k5-connect-router.py

![fig080](https://cloud.githubusercontent.com/assets/21165341/26093499/23dbed94-3a51-11e7-9db8-464309439df4.png)


ルータとnet01-port01を接続。

```
bash-4.4$ ./bin/k5-connect-router.py \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--port-id 430497b1-fdd4-4857-bc43-53286b5a27f5

status_code: 200
```

ルータとnet02-port01を接続。

```
bash-4.4$ ./bin/k5-connect-router.py \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--port-id bdab1ca6-fd32-4729-9e97-3827b72d7bc5

status_code: 200
```

<BR>

## 手順７．ネットワークコネクタを作成する

事業者が用意するネットワークコネクタプールを指定して、ネットワークコネクタを作成します。

- bin/k5-create-network-connector.py

ネットワークコネクタが外部の物理ネットワークとの境界になると考えられます。ネットワークコネクタに設定すべきパラメータは、申請書にもとづいて変更をかけていきます。

![fig090](https://cloud.githubusercontent.com/assets/21165341/26093448/f6268404-3a50-11e7-8cda-72f7469a752b.png)

```
bash-4.4$ ./bin/k5-create-network-connector.py \
--name iida-az1-nc \
--nc-pool-id e0a80446-203e-4b28-abec-d4b031d5b63e

POST /v2.0/network_connectors
=======  ====================================
name     iida-az1-nc
id       88f343e8-a956-4bcc-853f-3c40d53cbb49
pool_id  e0a80446-203e-4b28-abec-d4b031d5b63e
=======  ====================================
bash-4.4$
```

作成したネットワークコネクタの名前とID。

|name|network_connector_id|
|:--|:--|
|iida-az1-nc|88f343e8-a956-4bcc-853f-3c40d53cbb49|

<BR>

## 手順８．コネクタエンドポイントを作成する

ネットワークコネクタを指定してコネクタエンドポイントを作成します。
コネクタエンドポイントは論理ルータと同じイメージです。

- bin/k5-create-network-connector-endpoint.py

![fig100](https://cloud.githubusercontent.com/assets/21165341/26094065/5eb0f35e-3a53-11e7-8125-16e16935b329.png)

```
bash-4.4$ ./bin/k5-create-network-connector-endpoint.py
--name iida-az1-ncep \
--nc-id 88f343e8-a956-4bcc-853f-3c40d53cbb49

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

作成したコネクタエンドポイントの名前とID。

|name|network_connector_endpoint_id|
|:--|:--|
|iida-az1-ncep|848a40c2-7ded-4df8-a43d-e55b912811a2|

<BR>

## 手順９．コネクタエンドポイントとポートを接続する

作成済みのポートとコネクタエンドポイントを接続します。

- bin/k5-connect-network-connector-endpoint.py

![fig110](https://cloud.githubusercontent.com/assets/21165341/26093668/cef50dc8-3a51-11e7-9c3b-5be336eddb37.png)

```
bash-4.4$ ./bin/k5-connect-network-connector-endpoint.py \
--ncep-id 848a40c2-7ded-4df8-a43d-e55b912811a2 \
--port-id 6c73b1a0-ab3d-46e5-9515-f04e9f660423

status_code: 200
{'interface': {'port_id': '6c73b1a0-ab3d-46e5-9515-f04e9f660423'}}
```

<BR>

## 手順１０．ルータと外部ネットを接続する

ルータと外部ネットワークを接続します。
外部ネットワークの場合にはポートを経由しません。直接ネットワークを指定します。

- bin/k5-update-router.py

![fig120](https://cloud.githubusercontent.com/assets/21165341/26093743/14d2d2e4-3a52-11e7-826d-b1b752f12993.png)

```
bash-4.4$ ./bin/k5-update-router.py
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--network-id cd4057bd-f72e-4244-a7dd-1bcb2775dd67

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

- bin/k5-update-subnet.py
- conf/subnet.yaml

このスクリプトは設定パラメータが多いだけでなく、形式が複雑なので、YAML形式の設定ファイルを作って読み込ませます。
第一階層のキーは対象サブネットのIDを指定してください（最後のコロンを忘れないように）

> (自分メモ)
>
> キーはサブネットの名前にした方が使いやすいかも

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
bash-4.4$ ./bin/k5-update-subnet.py --subnet-id 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
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

> NOTE:
>
> 複数のルータを使う構成では、どの宛先はどのゲートウェイを使うか、という洗い出しを、全てのルータについて行わなければいけません。
>
> スタティックルーティングはたいへん面倒です。

- bin/k5-update-extra-routes.py
- conf/extra-routes.yaml

このスクリプトはYAML形式の設定ファイルを作って読み込ませます。

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
bash-4.4$ ./bin/k5-update-extra-routes.py \
--filename r1.yaml \
ffbd70be-24cf-4dff-a4f6-661bf892e313

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

K5と構内で接続するルータを別途用意します。

ネットワークコネクタの設定・変更は利用者ではできませんので、申請書にもとづいて手続きを進めます。

### コネクタエンドポイント自身のルーティング

コネクタエンドポイントはルータみたいなものですが、ルーティングを操作するためのAPIは公開されていません。
したがって、事業者に申請して設定を入れてもらうことになります。

![fig170](https://cloud.githubusercontent.com/assets/21165341/26152469/0754a1ba-3b42-11e7-97c2-e9c241e2cab5.png)

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

# ファイアウォールの設定と手順概要

> NOTE:
>
> 公開されているドキュメントを読んでもよくわからない部分があります。ここに記載していることは個人的な理解です。

> NOTE:
>
> ファイアウォールは最大何コネクションまで保持できるのか、公開資料ではみつけられませんでした。

<BR>

K5のネットワークではFWの利用が推奨となっています。

FWはネットワークの構成要素ではなく、ルータに付与される通信制限の機能です。
FWでセグメントを分割する、といったことはできません。

一般的なファイアウォール製品は物理ポートやセキュリティグループ、
inside/outsideといったアイデアを駆使して壁を作っていきますが、
K5のFWにはそれがなく、物理ポートを意識しない作りになっています。

FWaaSのファイアウォールは暗黙のdenyが入っていますので、適用すると全通信が遮断されます。この状態から必要な通信を許可していくわけですが、一定の制約事項を導入しないと設計が大変です。

K5内のネットワークにセキュリティレベルの概念を導入して、レベルの高いところから低いところ向けは無条件で許可、逆にレベルの低いところから高いところへの通信は全て遮断することにします。

このようにしておけば、サーバで待ち受けているポートへの着信通信をピンポイントで開けていくだけですみます。

たとえば、このようにセキュリティレベルを定義したとします。

![fig150](https://cloud.githubusercontent.com/assets/21165341/26094136/a87afdc2-3a53-11e7-932e-9081fb674efd.png)

インターネットは外部なのでセキュリティレベルは『最低』です。
net01はDMZを意識してレベルは『中』、
net02は内部ネットワークを意識してレベルは『高』、
その他のイントラネットはレベル『低』です。

この場合に定義すべきルールはこのようになります。

![fig160](https://cloud.githubusercontent.com/assets/21165341/26094186/df83fa30-3a53-11e7-84d3-54e699502757.png)

セキュリティレベル『高』には管理LANも入れておくとよいと思います。

<BR>

## 手順１４．ファイアウォールルールの作成

ファイアウォールのルールを作成しても何も起こりません。
安心して作ったり、消したりできます。

ルールの例です。

高→低（許可）

|項番|名前|アクション|プロトコル|送信元アドレス|送信元ポート|宛先アドレス|宛先ポート|
|:--|:--|:--|:--|:--|:--|:--|:--|
|1|iida-az1-p01-net02-any-tcp|allow|tcp|10.1.2.0/24|null|null|null|
|2|iida-az1-p01-net02-any-udp|allow|udp|10.1.2.0/24|null|null|null|
|3|iida-az1-p01-net02-any-icmp|allow|icmp|10.1.2.0/24|null|null|null|

中→高（遮断）

|項番|名前|アクション|プロトコル|送信元アドレス|送信元ポート|宛先アドレス|宛先ポート|
|:--|:--|:--|:--|:--|:--|:--|:--|
|4|iida-az1-p01-net01-net02-tcp|deny|tcp|10.1.1.0/24|null|10.1.2.0/24|null|
|5|iida-az1-p01-net01-net02-udp|deny|udp|10.1.1.0/24|null|10.1.2.0/24|null|
|6|iida-az1-p01-net01-net02-icmp|deny|icmp|10.1.1.0/24|null|10.1.2.0/24|null|

中→低（許可）

|項番|名前|アクション|プロトコル|送信元アドレス|送信元ポート|宛先アドレス|宛先ポート|
|:--|:--|:--|:--|:--|:--|:--|:--|
|7|iida-az1-p01-net01-net02-tcp|allow|tcp|10.1.1.0/24|null|null|null|
|8|iida-az1-p01-net01-net02-udp|allow|udp|10.1.1.0/24|null|null|null|
|9|iida-az1-p01-net01-net02-icmp|allow|icmp|10.1.1.0/24|null|null|null|

最低/低→中/高（遮断）

|項番|名前|アクション|プロトコル|送信元アドレス|送信元ポート|宛先アドレス|宛先ポート|
|:--|:--|:--|:--|:--|:--|:--|:--|
|10|deny-all-tcp|allow|tcp|null|null|null|null|
|11|deny-all-udp|allow|udp|null|null|null|null|
|12|deny-all-icmp|allow|icmp|null|null|null|null|


ここまでつくっておけば、あとは必要に応じて追加で穴あけをしていけばいいでしょう。
追加穴あけはこれらよりも先に評価されるようにルールの優先順位を指定します。

> NOTE:
>
> プロトコルにnullを指定するのはまずいようです。
> APIのマニュアルにはこのように記載されています。
>
> > Avoid the use of null when specifying the protocol for
> > Neutron FWaaS rules. Instead, create multiple rules for
> > both ‘tcp' and ‘udp' protocols independently.
>
> nullを指定できるのはアドレスとポートだけのようです。

> NOTE:
>
> フローティングIPを使った場合のルールは、対応するプライベートアドレスの方を使ってルールを書きます。フローティングIPは変わってしまうかもしれませんので、FWルールには使いません。

> NOTE:
>
> アプリケーションインスペクションの機能有無がわかりません。
>
> FTPを許可した場合、関連するFTP-DATAも自動で許可されるのか・・・

> NOTE:
>
> セキュリティグループにおいては、169.254.169.254/32 tcp/80の通信がポートから出ていけるように許可しないといけませんが、この通信はファイアウォールには着信しないと思いますので、特にケアする必要はないと思います（穴あけ不要だと思っています）。
>
> 違うかな？　ちょっと自信なし。

- bin/k5-create-fw-rule.py
- conf/fw-rules.xlsx

このスクリプトは、エクセルファイルを読み込みます（デフォルトではconf/fw-rules.xlsxから読みます）。
このような感じでルールをエクセルで作成します。

![fig190](https://cloud.githubusercontent.com/assets/21165341/26291242/f1369416-3ee7-11e7-987a-1a5aa8dbe43d.png)

スクリプトの引数で与えたルール名をエクセルファイルから探して、その情報でルールを作成します。--saveオプションを付けると作成したルールのIDをエクセルファイルに保存します（エクセルで開きっぱなしにするとエラーになるので要注意）。

実行例。

```
bash-4.4$ ./bin/k5-create-fw-rule.py --name iida-az1-p01-mgmt01-any-tcp --save
POST /v2.0/fw/firewall_rules
======================  ====================================
id                      04f9bbc2-34f3-4b88-8313-def1f6984a9a
name                    iida-az1-p01-mgmt01-any-tcp
enabled                 True
action                  allow
protocol                tcp
source_ip_address       192.168.246.0/24
source_port
destination_ip_address
destination_port
description             test
availability_zone       jp-east-1a
tenant_id               a5001a8b9c4a4712985c11377bd6d4fe
======================  ====================================
```

<BR>

## （参考）ファイアウォールルールの一括作成と一括削除

動作検証の段階ではルールを作っては削除して、を繰り返すと思います。
この手の操作は簡単にできるようにした方がいいですね。

ルールを一括で作成するにはこうします（↓）。
エクセルファイル中のIDが空白になっているルールを全て作成します。--saveオプションを付けて作成したIDをエクセルに反映させたほうが楽できます。

```
./bin/k5-create-fw-rule.py --name all --save
```

K5に登録されているルールのうち、未使用のものを一括で削除するにはこうします（↓）。
ポリシーに紐付いているルールは削除できませんので、--unusedオプションで未使用のものだけを表示して、それをそのまま削除コマンドの入力にします。

```
./bin/k5-list-fw-rules.py --unused | ./bin/k5-delete-fw-rule.py -
```

<BR>

## 手順１４．ファイアウォールポリシーの作成と変更と削除

ルールを作成したら、それを束ねるポリシーを作成します。
ポリシーを作成してもまだ何も起こりません。安心して作成したり、削除したりできます。

> NOTE:
>
> ルールをポリシーに紐付けると、ルールの削除ができなくなります。
> ルールを削除したければまずポリシーから外す必要があります。

ポリシーを作成してからルールを順次追加していく方法もありますが、
ここではエクセルファイルで作成したルールを一括してポリシーに紐付ける方法でやってみます。

- bin/k5-create-fw-policy.py
- conf/fw-rules.xlsx

このスクリプトはエクセルファイルのfirewall_policy_id列が未記入のものをそのポリシーで使うルールにします。

実行例。

```
bash-4.4$ ./bin/k5-create-fw-policy.py --name p1 --filename ./data/p1.xlsx --save
/v2.0/fw/firewall_policies
=================  ====================================
id                 3e500de7-5d7c-4585-954f-f911e077fa58
name               p1
availability_zone  jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
=================  ====================================
====================================
114d70cc-3c3c-4e17-a85c-fa995a084f44
1d048151-593e-4c16-87cc-ba37fb55a811
1583ce48-608c-429e-92cf-a82471929111
f89e509f-9cea-4587-bba6-63163ab41c73
79ca78c3-6905-4dde-9ff2-e26c1f9091e0
21fc602c-5aa1-4bdd-b145-7f4872e7e470
a9e5141a-8b29-408c-98c6-c64efb2437de
29ad528b-f868-49ee-bc84-6034f960dcba
07773c9a-6dd9-45f4-8722-ddfbf2981515
8bd856d6-1ee1-4402-a69b-65c3381d5c26
cf17f5bf-398e-4602-937d-a4da6b07a162
3158c601-4ce7-40ef-9efa-cee09968951e
====================================
bash-4.4$
```

ポリシーの一覧を表示すると、12個のルールを持っていることがわかります。

```
bash-4.4$ ./bin/k5-list-fw-policies.py
GET /v2.0/fw/firewall_policies
====================================  ======  ==============  ================================  ==========
id                                    name      num of rules  tenant_id                         az
====================================  ======  ==============  ================================  ==========
3e500de7-5d7c-4585-954f-f911e077fa58  p1                  12  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ======  ==============  ================================  ==========
```

ルールを表示すると、positionが割り当てられていて、エクセルファイルに記載の順にルールが登録されていることがわかります。

```
bash-4.4$ ./bin/k5-list-fw-rules.py
policy : 3e500de7-5d7c-4585-954f-f911e077fa58
====================================  =============================  ==========  ========  ==========  ===================
id                                    name                             position  action    protocol    availability_zone
====================================  =============================  ==========  ========  ==========  ===================
114d70cc-3c3c-4e17-a85c-fa995a084f44  iida-az1-p01-net02-any-tcp              1  allow     tcp         jp-east-1a
1d048151-593e-4c16-87cc-ba37fb55a811  iida-az1-p01-net02-any-udp              2  allow     udp         jp-east-1a
1583ce48-608c-429e-92cf-a82471929111  iida-az1-p01-net02-any-icmp             3  allow     icmp        jp-east-1a
f89e509f-9cea-4587-bba6-63163ab41c73  iida-az1-p01-net01-net02-tcp            4  deny      tcp         jp-east-1a
79ca78c3-6905-4dde-9ff2-e26c1f9091e0  iida-az1-p01-net01-net02-udp            5  deny      udp         jp-east-1a
21fc602c-5aa1-4bdd-b145-7f4872e7e470  iida-az1-p01-net01-net02-icmp           6  deny      icmp        jp-east-1a
a9e5141a-8b29-408c-98c6-c64efb2437de  iida-az1-p01-net01-any-tcp              7  allow     tcp         jp-east-1a
29ad528b-f868-49ee-bc84-6034f960dcba  iida-az1-p01-net01-any-udp              8  allow     udp         jp-east-1a
07773c9a-6dd9-45f4-8722-ddfbf2981515  iida-az1-p01-net01-any-icmp             9  allow     icmp        jp-east-1a
8bd856d6-1ee1-4402-a69b-65c3381d5c26  deny-all-tcp                           10  deny      tcp         jp-east-1a
cf17f5bf-398e-4602-937d-a4da6b07a162  deny-all-udp                           11  deny      udp         jp-east-1a
3158c601-4ce7-40ef-9efa-cee09968951e  deny-all-icmp                          12  deny      icmp        jp-east-1a
====================================  =============================  ==========  ========  ==========  ===================
```


作成したポリシーから、ルールを削除したり、追加したり、順番を変更するには、エクセルファイルを編集してポリシーにアップデートをかけます。

特定のルールをポリシーから外す場合は、firewall_policy_idの値を空白にします。
復活させたい場合や、新たにルールを追加したい場合は、firewall_policy_idを埋めてからアップデートします。

実行例。ここでは12個のルールのうち、9個のルールをポリシーから外しました。

```
bash-4.4$ ./bin/k5-update-fw-policy.py --filename ./data/p1.xlsx 3e500de7-5d7c-4585-954f-f911e077fa58
/v2.0/fw/firewall_policies
=================  ====================================
id                 3e500de7-5d7c-4585-954f-f911e077fa58
name               p1
availability_zone  jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
=================  ====================================
====================================
8bd856d6-1ee1-4402-a69b-65c3381d5c26
cf17f5bf-398e-4602-937d-a4da6b07a162
3158c601-4ce7-40ef-9efa-cee09968951e
====================================
bash-4.4$
```

ルールの一覧を確認すると、未使用(unused)のものが9個、ポリシー(*3e500de7-5d7c-4585-954f-f911e077fa58*)に紐付いたルールが3個あることがわかります。

```
bash-4.4$ ./bin/k5-list-fw-rules.py
policy : unused
====================================  =============================  ==========  ========  ==========  ===================
id                                    name                           position    action    protocol    availability_zone
====================================  =============================  ==========  ========  ==========  ===================
07773c9a-6dd9-45f4-8722-ddfbf2981515  iida-az1-p01-net01-any-icmp                allow     icmp        jp-east-1a
114d70cc-3c3c-4e17-a85c-fa995a084f44  iida-az1-p01-net02-any-tcp                 allow     tcp         jp-east-1a
1583ce48-608c-429e-92cf-a82471929111  iida-az1-p01-net02-any-icmp                allow     icmp        jp-east-1a
1d048151-593e-4c16-87cc-ba37fb55a811  iida-az1-p01-net02-any-udp                 allow     udp         jp-east-1a
21fc602c-5aa1-4bdd-b145-7f4872e7e470  iida-az1-p01-net01-net02-icmp              deny      icmp        jp-east-1a
29ad528b-f868-49ee-bc84-6034f960dcba  iida-az1-p01-net01-any-udp                 allow     udp         jp-east-1a
79ca78c3-6905-4dde-9ff2-e26c1f9091e0  iida-az1-p01-net01-net02-udp               deny      udp         jp-east-1a
a9e5141a-8b29-408c-98c6-c64efb2437de  iida-az1-p01-net01-any-tcp                 allow     tcp         jp-east-1a
f89e509f-9cea-4587-bba6-63163ab41c73  iida-az1-p01-net01-net02-tcp               deny      tcp         jp-east-1a
====================================  =============================  ==========  ========  ==========  ===================

policy : 3e500de7-5d7c-4585-954f-f911e077fa58
====================================  =============  ==========  ========  ==========  ===================
id                                    name             position  action    protocol    availability_zone
====================================  =============  ==========  ========  ==========  ===================
8bd856d6-1ee1-4402-a69b-65c3381d5c26  deny-all-tcp            1  deny      tcp         jp-east-1a
cf17f5bf-398e-4602-937d-a4da6b07a162  deny-all-udp            2  deny      udp         jp-east-1a
3158c601-4ce7-40ef-9efa-cee09968951e  deny-all-icmp           3  deny      icmp        jp-east-1a
====================================  =============  ==========  ========  ==========  ===================
```

ファイアウォールポリシーそのものを削除するにはこうします。
一つしか作っていないときには、いちいちIDを調べなくてすむこのやり方が便利です。

```
bash-4.4$ ./bin/k5-list-fw-policies.py | ./bin/k5-delete-fw-policy.py -
b851c88d-ca26-4218-9b9a-75490708f0df
status_code: 204

```

<BR>

## 手順１５．ルータにファイアウォールを紐付け

最終段階です。
作成済みのルータと、作成済みのポリシーを指定して、ファイアウォールを作成します。

ルータIDとポリシーIDがこう（↓）なっている前提で作成してみます。

```
bash-4.4$ ./bin/k5-list-routers.py
GET /v2.0/routers
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
ffbd70be-24cf-4dff-a4f6-661bf892e313  iida-az1-router01  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========


bash-4.4$ ./bin/k5-list-fw-policies.py
GET /v2.0/fw/firewall_policies
====================================  ======  ==============  ================================  ==========
id                                    name      num of rules  tenant_id                         az
====================================  ======  ==============  ================================  ==========
3e500de7-5d7c-4585-954f-f911e077fa58  p1                   3  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a
====================================  ======  ==============  ================================  ==========
```

- bin/k5-create-firewall.py

実行例。

```
bash-4.4$ ./bin/k5-create-firewall.py \
--policy-id 3e500de7-5d7c-4585-954f-f911e077fa58 \
--router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 \
--name fw1

/v2.0/fw/firewalls
==================  ====================================
id                  006b796d-9a07-4674-9fd3-34ff53b59ea0
name                fw1
router_id           ffbd70be-24cf-4dff-a4f6-661bf892e313
firewall_policy_id  3e500de7-5d7c-4585-954f-f911e077fa58
status              PENDING_CREATE
availability_zone   jp-east-1a
tenant_id           a5001a8b9c4a4712985c11377bd6d4fe
==================  ====================================
bash-4.4$
```

作成直後はPENDING_CREATEという状態になるようですが、すぐにACTIVEに変わります。

```
bash-4.4$ ./bin/k5-list-firewalls.py
/v2.0/fw/firewalls
====================================  ======  ====================================  ====================================  ========
id                                    name    router_id                             firewall_policy_id                    status
====================================  ======  ====================================  ====================================  ========
006b796d-9a07-4674-9fd3-34ff53b59ea0  fw1     ffbd70be-24cf-4dff-a4f6-661bf892e313  3e500de7-5d7c-4585-954f-f911e077fa58  ACTIVE
====================================  ======  ====================================  ====================================  ========
bash-4.4$
```

> NOTE:
>
> この状態でポリシーの内容変更は可能ですが、通信中のコネクションには反映されません。
> 新規コネクションから新しいポリシーが適用されます。

<BR>

> NOTE:
>
> 通過中のコネクションを全て強制切断するには、bin/k5-reset-firewall.pyを使います。

<BR>

> NOTE:
>
> 利用中のポリシーは削除できません。ポリシーのデタッチはできませんので、先にファイアウォール自体を削除します。


<BR>
<BR>

# フローティングIP

フローティングIPは外部ネットワークのグローバルIPと内部ネットワークのプライベートIPを１対１に対応付けるものです。

## フローティングIPの作成

事前に準備すべき情報が多いので整理が必要です。

まず最初に利用する外部ネットワークです。
仮想ルータのexternal_gateway_infoに設定した外部ネットワークのIDが必要です。

ルータの情報を確認してみます。
ルータを一つしか作成していないなら名前もIDも必要ありません。
このコマンドで確認できます。

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

external_gateway_infoの部分に書かれているnetwork_idが外部ネットワークのIDです。

- 外部ネットワークのID = cd4057bd-f72e-4244-a7dd-1bcb2775dd67

次に内部ネットワークに接続している空きポートの情報が必要です。
無ければ作成しましょう。
iida-az1-net01に新規ポートを作成したいので、その情報を調べます。

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

- 内部ネットワークのID = 8f15da62-c7e5-47ec-8668-ee502f6d00d2
- そのサブネットのID = abbbbcf4-ea8f-4218-bbe7-669231eeba30

ということがわかります。
それでは固定IPアドレスを 10.1.1.100としてポートを作成してみます。


```
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
```

- ポートのID = 77297e3a-7135-4fb4-8024-e677d9df66d4

これで必要な情報が出揃いましたので、フローティングIPを作成します。

- bin/k5-create-floatingip.py

引数 --network-idにはグローバルIPアドレスを払い出す外部ネットワークのIDを指定します。

引数 --port-idには内側の空きポートを指定します。

引数 --fixed_ip_addressにはそのポートに付与した固定IPを指定します。

```
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
```

無事にフローティングIPが作成されました。
外からみた133.162.215.230は内側の10.1.1.100と１対１に対応します。

今使っているフローティングIPを別のポートに移したい、という場合もあると思います。
その場合は、
- bin/k5-update-floatingip.py
コマンドを使います。

実行例。

```
bash-4.4$ ./bin/k5-update-floatingip.py \
--floatingip-id 5654254d-0f36-425d-ae89-6e827fc99e54 \
--port-id 6ec9de23-9e3c-4cf1-99be-f3b84b915b24

/v2.0/floatingips
===================  ====================================
id                   5654254d-0f36-425d-ae89-6e827fc99e54
floating_ip_address  133.162.215.230
fixed_ip_address     10.1.1.200
status               DOWN
port_id              6ec9de23-9e3c-4cf1-99be-f3b84b915b24
router_id            ffbd70be-24cf-4dff-a4f6-661bf892e313
availability_zone    jp-east-1a
tenant_id            a5001a8b9c4a4712985c11377bd6d4fe
===================  ====================================
bash-4.4$
```

不要になったフローティングIPを削除するなら、
- bin/k5-delete-floatingip.py
コマンドを使います。

実行例。

```
bash-4.4$ ./bin/k5-list-floatingips.py | ./bin/k5-delete-floatingip.py -
status_code: 204
```

<BR>
<BR>

# K5ネットワークの制限事項

公開されている情報をメモしておきます。
制限は解除されたり変更される可能性がありますので、気になる制限事項は引用元を確認してください。

<BR>

## [IaaS 制限事項・注意事項](http://jp.fujitsu.com/solutions/cloud/k5/document/pdf/k5-limitation.pdf)

- K5構内接続とダイレクトポート接続に利用するネットワークコネクタは併用できない

- **ネットワークコネクタは1階層ネットワークのみ利用可能**　（★１）下記補足参照

- 多階層ネットワーク上の仮想サーバからインターネットへの通信はできない（おそらくNATの都合）

- Microsoft NLBは利用できない

- IPsec VPNの最大拠点数は20拠点

- SSL-VPNの最大同時接続数は20セッション

- ロードバランサのIPアドレスは変更される可能性があるため、付与されたFQDNでアクセスする

- ロードバランサに付与されたFQDN名はDNSサービスに自動登録される

- 仮想サーバにグローバルIPアドレスを付与した際は、利用者が任意のFQDN名をDNSサービスに登録する（手動）

- ロードバランサのCookieExpirationPeriodは、初回アクセスからの経過時間

- ロードバランサはグレードごとに必要なIPが異なる（Standard：4個、Middle：8個、High：12個）

- 仮想サーバから仮想ルータを経由して169.254.169.254/32 tcp/80との通信ができるよう、セキュリティグループとルーティングを設定する

- データベース仮想サーバに割り当てるセキュリティグループには、そのセキュリティグループ自身に対するデータベース用ポートの送受信を許可する設定を含める

<BR>

### （★１）ネットワークコネクタは1階層ネットワークのみ利用可能 についての補足

ネットワークコネクタを使って異なるAZ間を接続する場合に、通信できるのは1階層のみ、ということだと思われます。
ネットワークコネクタ自体へのルーティング設定は利用者に公開されていませんので、自足経路の通信しかできない、ということだと思います。
（構内接続と同じように事業者に申請すればいいのでは？　という気もしますが）

![fig180](https://cloud.githubusercontent.com/assets/21165341/26231168/9bc7fb7a-3c88-11e7-9281-89c751cd6256.png)


<BR>

## [機能説明書](https://k5-doc.jp-east-1.paas.cloud.global.fujitsu.com/doc/jp/iaas/document/k5-iaas-function-manual.pdf)

5.2.1 ポート管理

- 仮想サーバに割り当てられたポートのMACアドレス、IPアドレスの組み合わせ以外の通信を遮断するフィルタが自動設定されます。→飯田注：VRRPやHSRPのような仮想IP/仮想MACを使うものは、ポートに追加設定が必要、ということです。なおMicrosoft NLBの利用は禁止されています。


A.1 制限値

- ネットワーク数は1プロジェクト内で、1アベイラビリティゾーン
ごとに10

- サブネット数は1プロジェクト内で、1アベイラビリティゾーン
ごとに10

- サブネットに設定可能なホストルート数は、1プロジェクト内で20

- ポート数は、1プロジェクト内で、1アベイラビリティゾーンごとに50

- ポートに設定可能な通信許可アドレスペア数は、1プロジェクト内で、1アベイラビリティゾーンごとに10

- グローバルIPアドレス数は、1プロジェクト内で、1アベイラビリティゾーンごとに50

- セキュリティグループ数は、1プロジェクト内で20

- セキュリティグループに設定可能なルール数は、1プロジェクト内で100（個々のセキュリティグループに設定可能な数ではありません）

- 仮想ルータ数1は、プロジェクト内で、1アベイラビリティゾーンごとに10

- 仮想ルータに設定可能なルーティング数は、128／仮想ルータ

- ファイアーウォール数は、1プロジェクト内で、1アベイラビリティゾーンごとに10

- ファイアーウォールポリシー数は、1／ファイアーウォール

- ファイアーウォールルール数は、500／ファイアーウォールポリシー


<BR>

## [APIリファレンス（Network編）](https://k5-doc.jp-east-1.paas.cloud.global.fujitsu.com/doc/jp/iaas/document/k5-iaas-api-reference_network.pdf)

1.1.6.7 Create subnet

- ISP shared address(100.64.0.0/10あるいは、そのサブネットを分割したサブネットアドレス)は指定しないでください。


1.1.6.10 Delete subnet

- Subnetをdelete した場合は、Subnetが作成されていたNetworkでDHCPが使えなくなります。DHCP利用時はSubnetを単体でdeleteせず、Networkもdeleteしてください。


<BR>

## [クラウドデザインパターン](https://k5-doc.jp-east-1.paas.cloud.global.fujitsu.com/doc/jp/iaas/document/cdp/SecurityGroup_and_FW.html)

セキュリティグループ/ファイアーウォール併用パターン

- ロードバランサのIPアドレスは変更されることがあるため、セキュリティグループでアクセス制御することを推奨します。ファイアーウォールのみでアクセス制御することは推奨しません。

- セキュリティグループやファイアーウォールのルールの変更時、既に張られているセッションはルールを変更後もセッションが残ります。

  - DoS攻撃などで特定IPアドレスからの通信を拒否したい場合も、セッションが残っている間は新たなルールが適用されません。通信が許可されている状態です。

  - ルール変更後に張られた新規セッションは正常に拒否されます。

  - ファイアーウォールのルール適用時の全セッション強制切断機能は提供済です。


<BR>
<BR>

# スクリプトについて

<BR>

## Python実行環境と依存モジュール

Pythonはversion 3を想定しています。

以下のモジュールを利用しています。
lib/site-packagesにこれらを含めていますので、インストールは不要です。

 - requests
 - tabulate
 - pyyaml
 - openpyxl

<BR>

## 事前に必要な情報

- K5管理者のユーザ名
- K5管理者のパスワード
- ドメイン名(契約番号と同じ)
- プロジェクトID(32桁英数字)
- グループ内のドメインID(32桁英数字)
- リージョン名(例：jp-east-1)

この他、必要に応じてプロキシサーバの情報が必要です。

<BR>

## ディレクトリ構成


```
k5c
├─bin
├─conf
├─lib
│  ├─k5c
│  └─site-packages
│      ├─et_xmlfile
│      ├─openpyxl
│      ├─requests
│      └─yaml
└─log
```

<BR>

## 設定ファイル

conf/_k5config.ini のファイル名を k5config.ini に変更して、適宜書き換えてください。

k5config.ini

```ini
[k5]

# K5関連設定

# 契約番号 ★ここを書き換え
# 例：DOMAIN_NAME = fXXXXXi
DOMAIN_NAME =

# ドメインID(32桁) ★ここを書き換え
# IaaSポータルから[管理]→[利用者管理]→[グループ]
# 例：DOMAIN_ID = exxxxxxxxxxxxxxxxxxxxxxxxxxxxxxc
DOMAIN_ID =

# プロジェクトID(32桁) ★ここを書き換え
# 別名テナントID
# 例：PROJECT_ID = exxxxxxxxxxxxxxxxxxxxxxxxxxxxxxc
PROJECT_ID =

# ユーザ情報 ★ここを書き換え
USERNAME =
PASSWORD =

# 対象リージョン
REGION = jp-east-1

[proxy]

# プロキシ設定

# True or False
USE_PROXY = False

HTTP_PROXY = http://username:password@proxy-server-address:8080
HTTPS_PROXY = http://username:password@proxy-server-address:8080

[requests]

# requestsモジュール関連設定

TIMEOUT = 15

[k5c]

# k5cモジュールの設定

# True or False
USE_FILE_HANDLER = True
```

<BR>

## スクリプトの実行

binフォルダに実行用のスクリプトを置いています。

Windowsのコマンドプロンプトでも実行できますが、画面の横幅が狭いため見苦しい表示になってしまいます。
TeraTERMでCygwinに接続する、出力をファイルにリダイレクトしてエディタで確認する、といった工夫をするといいと思います。

### k5-token.py

APIエンドポイントに接続できるかテストするためのスクリプトで、通常は使いません。
これがエラーを返すようなら、k5config.iniが存在しないか、k5config.iniの設定パラメータに誤りがあります。

```
bash-4.4$ ./bin/k5-token.py
{
  "expires_at": "2017-05-02T13:31:28.092961Z",
  "X-Subject-Token": "f240eccd302f4a31b3ccdb4b0d1bcd7f",
  "issued_at": "2017-05-02T10:31:28.092987Z"
}
```

時刻はISO 8601形式のUTCになっています。
issued_atとexpires_atの差分が3時間ほどありますので、トークンの有効期間は3時間であることが確認できます（マニュアルにも書いてあります）。
トークンは取得するたびに変わります。
払い出せるトークンの数には制限がありますので、一度取得したトークンはキャッシュして使いまわすようにしています。


### k5-list-xxx.py

一覧表示します。

### k5-create-xxx.py

作成します。

### k5-delete-xxx.py

削除します。

### k5-show-xxx.py

詳細表示します。

### k5-update-xxx.py

更新します。

### k5-connect-router.py

ルータとポートを接続します。

### k5-disconnect-router.py

ルータとポートを切り離します。

> NOTE:
>
> 実行すると、なぜかポート自体が削除されます。ポートを作り直してください。

### k5-connect-network-connector-endpoint.py

コネクターエンドポイントを内部ネットワークに接続します。

### k5-disconnect-network-connector-endpoint.py

コネクターエンドポイントと内部ネットワークを切り離します。
