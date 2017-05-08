# k5c

K5のネットワーク環境を操作するためのPythonスクリプト集です。


## K5ネットワークの基礎知識

### ネットワークとサブネットとポートの関係

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


### ネットワークコネクタ

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

ネットワークコネクタには、コネクタエンドポイントを作成します。これが内側との接点になります。ポートのオーナーとしてコネクタエンドポイントを指定することで、内側のネットワークと紐付けられます。

ネットワークコネクタには複数のコネクタエンドポイントを作成できます。したがって、一つの構内接続を複数のプロジェクトで共有することもできます。

外部との接続を作成する順番としては、このようになります。

1. ネットワークコネクタプールのIDを調べる
2. そのプールのIDを指定して、ネットワークコネクタを作成する
3. 作成したネットワークコネクタのIDを調べる
4. そのネットワークコネクタのIDを指定してコネクタエンドポイントを作成する
5. 事前に作成しておいたポートのオーナーとしてコネクタエンドポイントを指定する



## Pythonのバージョンと依存モジュール

Pythonはversion 3を想定しています。

以下のモジュールを利用しています。
lib/site-packagesにこれらを含めていますので、インストールは不要です。

 - requests
 - tabulate


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

# グループdomainmanagerのドメインID
DOMAIN_ID = ""  # ここを書き換え

# プロジェクトID
PROJECT_ID = ""  # ここを書き換え

# ユーザ情報
USERNAME = ""  # ここを書き換え
PASSWORD = ""  # ここを書き換え

# 利用リージョン
REGION = "jp-east-1"  # ここを書き換え
```

---

## スクリプトの実行

scriptsフォルダに実行用のスクリプトを置いています。

k5-create-系のスクリプトは、作成に必要なパラメータをスクリプト本文に埋め込んでいますので、環境にあわせて修正が必要です（後で直します）。

Windowsのコマンドプロンプトでも実行できますが、画面の横幅が狭いため見苦しい表示になってしまいます。
TeraTERMでCygwinに接続する、出力をファイルにリダイレクトしてエディタで確認する、といった工夫をするといいと思います。

K5のAPIを操作するためには、事前に認証トークンを取得しなければいけませんが、このスクリプトはトークンを気にせず使えます。
スクリプト実行時に有効なトークンがキャッシュされていればそれを使います。
トークンのキャッシュがない、あるいは有効期限が切れている場合には、REST API実行前にトークンを自動的に取りにいきます。


### k5-token.py

APIエンドポイントに接続できるかテストするためのスクリプトで、通常は使いません。
これがエラーを返すようなら、k5config.pyの設定パラメータに誤りがあります。

```
bash-4.4$ ./k5-token.py
{
  "expires_at": "2017-05-02T13:31:28.092961Z",
  "X-Subject-Token": "f240eccd302f4a31b3ccdb4b0d1bcd7f",
  "issued_at": "2017-05-02T10:31:28.092987Z"
}
```

issued_atとexpires_atの差分が3時間ほどありますので、トークンの有効期間は3時間と考えられます。
トークンは取得するたびに変わります。
払い出せるトークンの数には制限があるかもしれませんので、
一度取得したトークンはキャッシュして使いまわすようにしています。

（自分用メモ：expires_atはGMTになっているので、ローカル時間に直す処理が必要。別途実装すること）


### k5-list-network-connector-pools.py

ネットワークコネクタプールは事業者が作成するもので、そのIDを調べるためにこのスクリプトを使います。

- GET /v2.0/network_connector_pools
- List Network Connector Pools
- ネットワークコネクタプールの一覧を表示する

```
bash-4.4$ ./k5-list-network-connector-pools.py
GET /v2.0/networks
====================================  ============================
id                                    name
====================================  ============================
e0a80446-203e-4b28-abec-d4b031d5b63e  jp-east-1a_connector_pool_01
====================================  ============================
```

jp-east-1a_connector_pool_01という名前で一つ作成されていることがわかります。

### k5-create-network-connector.py

外部との接点になるネットワークコネクタを作成します。

- POST /v2.0/network_connectors
- Create Network Connector
- ネットワークコネクタを作成する

所属させるネットワークコネクタプールのIDを先に調べる必要があります。
ここでは *e0a80446-203e-4b28-abec-d4b031d5b63e* のコネクタプールに作成するとして、それをスクリプト本文で指定しています。

ネットワークコネクタの名前は *iida-test-network-connecotor* として、それをスクリプト本文で指定しています。

```
bash-4.4$ ./k5-create-network-connector.py
POST /v2.0/network_connectors
=======  ====================================
name     iida-test-network-connecotor
id       385bc7f5-bcc4-4521-ad41-de2074143355
pool_id  e0a80446-203e-4b28-abec-d4b031d5b63e
=======  ====================================
```

### k5-list-network-connectors.py

ネットワークコネクタを作成したら、一覧表示で確認します。

- GET /v2.0/network_connectors
- List Network Connectors
- ネットワークコネクタの一覧を表示する

```
bash-4.4$ ./k5-list-network-connectors.py
GET /v2.0/network_connectors
====================================  ============================  ====================================
id                                    name                          pool_id
====================================  ============================  ====================================
eceb05fd-8aee-470b-bdca-95f789f181c1  iida-test-network-connecotor  e0a80446-203e-4b28-abec-d4b031d5b63e
====================================  ============================  ====================================
```

### k5-create-network-connector-endpoint.py

ネットワークコネクタにコネクタエンドポイントを作成します。

事前にネットワークコネクタを作成しておく必要があります。
ここではid= *eceb05fd-8aee-470b-bdca-95f789f181c1* のコネクタの中に作成するものとして、スクリプト本文で指定しています。

コネクタエンドポイントの名前は *iida-test-network-connecotor-endpoint-1* として、スクリプト本文で指定しています。

- POST /v2.0/network_connector_endpoints
- Create Network Connector Endpoint
- ネットワークコネクタエンドポイントを作成する

```
bash-4.4$ ./k5-create-network-connector-endpoint.py
POST /v2.0/network_connector_endpoints
=============  =======================================
name           iida-test-network-connecotor-endpoint-1
id             ed44d452-cbc4-4f4c-9c87-03fdf4a7c965
nc_id          eceb05fd-8aee-470b-bdca-95f789f181c1
tenant_id      a5001a8b9c4a4712985c11377bd6d4fe
location       jp-east-1a
endpoint_type  availability_zone
=============  =======================================
```

作成に失敗するとこのような表示になります。

```
bash-4.4$ ./k5-create-network-connector-endpoint.py
{
  "Content-Type": "application/json;charset=utf-8",
  "status_code": 409,
  "data": {
    "NeutronError": {
      "type": "EndpointAlreadyExist",
      "detail": "network connector id: eceb05fd-8aee-470b-bdca-95f789f181c1, type: availability_zone, location: jp-east-1a",
      "message": "network connector endpoint already exist"
    },
    "request_id": "a79772bc-a08c-40b9-ae52-922857e29ff6"
  }
}
```

一つのコネクタには、一つのエンドポイントしか作成できないことがわかります。


### k5-create-network.py

K5の内部ネットワークを作成します。
ネットワークとサブネットは1:1の対応になります。

- POST /v2.0/networks
- Create network
- ネットワークを作成する

名前を *iida-test-network-1* とし、Availability Zone *jp-east-1a* としてネットワークを作成する例です。
これらパラメータはスクリプト本文で指定しています。

```
bash-4.4$ ./k5-create-network.py
POST /v2.0/networks
=========  ====================================
name       iida-test-network-1
id         93a83e0e-424e-4e7d-8299-4bdea906354e
az         jp-east-1a
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
```

同じ名前のネットワークも作れてしまいます。
同じ名前だとわかりづらくなるので、一意に区別できる意味のある名前が好ましいでしょう。


### k5-list-networks.py

ネットワークを作成したら、一覧で確認します。

- GET /v2.0/networks
- List networks
- テナントがアクセスするネットワークの一覧を表示する

```
bash-4.4$ ./k5-list-networks.py
GET /v2.0/networks
====================================  ===================  ================================  ==========  ========
id                                    name                 tenant_id                         az          status
====================================  ===================  ================================  ==========  ========
375c49fa-a706-4676-b55b-2d3554e5db6a  inf_az2_ext-net01    31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
4516097a-84dd-476f-824a-6b2fd3cc6499  inf_az2_ext-net05    31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
852e40a7-82a3-4196-8b84-46f55d01ccba  inf_az2_ext-net02    31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
abe76a93-87c3-4635-b0f3-40f794165c26  inf_az2_ext-net03    31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
bfca06b3-0b23-433f-96af-4f54bf963e5f  inf_az2_ext-net04    31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
93a83e0e-424e-4e7d-8299-4bdea906354e  iida-test-network-1  a5001a8b9c4a4712985c11377bd6d4fe  jp-east-1a  ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05    31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
====================================  ===================  ================================  ==========  ========
```

何やらたくさんネットワークがありますが、名前が *inf_* で始まるものは最初から存在するもので、インターネット向けのものです。
*iida-test-network-1* という名前で作成したものは *93a83e0e-424e-4e7d-8299-4bdea906354e* というIDになっていることが確認できます。


### k5-create-subnet.py

ネットワークと1:1に対応するサブネットを作成します。

- POST /v2.0/subnets
- Create subnet
- 指定したネットワーク上のサブネットを作成する


ネットワークIDは *93a83e0e-424e-4e7d-8299-4bdea906354e* に紐付けます。

名前は *iida-subnet-1* とします。

アドレス(cidr)は *192.168.0.0/24* とします。

```
bash-4.4$ ./k5-create-subnet.py
POST /v2.0/subnets
===========  ====================================
name         iida-subnet-1
id           38701f66-4610-493f-9c15-78f81917f362
az           jp-east-1a
cidr         192.168.0.0/24
gateway_ip   192.168.0.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   93a83e0e-424e-4e7d-8299-4bdea906354e
enable_dhcp  True
===========  ====================================
```

ゲートウェイのIPアドレスは *192.168.0.1* が自動で選ばれています。
指定しない場合はdhcpが有効になります。


### k5-show-network.py

特定のネットワークの情報を表示します。

- GET /v2.0/networks/{network_id}
- Show network
- 指定したネットワークの情報を表示する

作成したネットワーク *93a83e0e-424e-4e7d-8299-4bdea906354e* について表示すると、このようになります。

```
bash-4.4$ ./k5-show-network.py 93a83e0e-424e-4e7d-8299-4bdea906354e
GET /v2.0/networks/{network_id}
===================  ====================================  ==========  ========
name                 id                                    az          status
===================  ====================================  ==========  ========
iida-test-network-1  93a83e0e-424e-4e7d-8299-4bdea906354e  jp-east-1a  ACTIVE
===================  ====================================  ==========  ========

====================================
subnets
====================================
38701f66-4610-493f-9c15-78f81917f362
====================================
```

サブネットが一つ、対応付けられていることが確認できます。


### k5-show-subnet.py

特定のサブネットの情報を表示します。

- GET /v2.0/subnets/{subnet_id}
- Show subnet
- 指定したサブネットの情報を表示する

作成時に得られる情報と同じものが得られます。

```
bash-4.4$ ./k5-show-subnet.py 38701f66-4610-493f-9c15-78f81917f362
GET /v2.0/subnets/{subnet_id}
===========  ====================================
name         iida-subnet-1
id           38701f66-4610-493f-9c15-78f81917f362
az           jp-east-1a
cidr         192.168.0.0/24
gateway_ip   192.168.0.1
tenant_id    a5001a8b9c4a4712985c11377bd6d4fe
network_id   93a83e0e-424e-4e7d-8299-4bdea906354e
enable_dhcp  True
===========  ====================================
```

### k5-create-port.py

ネットワーク配下にサブネットを紐付けた後、ポートを作成します。

- POST /v2.0/ports
- Create port
- ポートを作成する

ネットワークIDは *93a83e0e-424e-4e7d-8299-4bdea906354e* (iida-test-network-1)の中に作成します。

このネットワークにはサブネットID *38701f66-4610-493f-9c15-78f81917f362* (iida-subnet-1)が紐付けられています。
このサブネットは *192.168.0.0/24* のアドレスを持っています。

固定IPアドレスとして *192.168.0.100* を指定して作成します。

```
bash-4.4$ ./k5-create-port.py
POST /v2.0/ports
=================  ====================================
name               iida-network-1-port-1
id                 802c2a2d-5e3e-41c8-8a94-c6430bf48a80
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             DOWN
admin_state_up     True
device_owner
device_id
network_id         93a83e0e-424e-4e7d-8299-4bdea906354e
binding:vnic_type  normal
mac_address        fa:16:3e:49:02:6d
=================  ====================================

=============  ====================================
ip_address     subnet_id
=============  ====================================
192.168.0.100  38701f66-4610-493f-9c15-78f81917f362
=============  ====================================
```

MACアドレスは自動採番され、 *fa:16:3e:49:02:6d* が割り当てられました。
オーナーとなるデバイスがまだ存在しませんので、device_ownerは空白です。


### k5-connect-network-connector-endpoint.py

ネットワークコネクタエンドポイントにポートを紐付けます。

- PUT /v2.0/network_connector_endpoints{network connector endpoint id}/connect
- Connect Network Connector Endpoint
- ネットワークコネクタエンドポイントにインターフェイスを接続する

コネクターエンドポイントID *ed44d452-cbc4-4f4c-9c87-03fdf4a7c965* (iida-test-network-connecotor-endpoint-1)にポートを割り当てます。

ポートは事前に作成しておいた *863f2404-4a92-4991-8fab-e4312682dd86* (iida-network-1-port-1)を使います。

```
bash-4.4$ ./k5-connect-network-connector-endpoint.py
status_code: 200
{'interface': {'port_id': '863f2404-4a92-4991-8fab-e4312682dd86'}}
```

ステータスコード200が返ってくれば成功です。

この状態でポートの情報を調べます。

```
bash-4.4$ ./k5-show-port.py 863f2404-4a92-4991-8fab-e4312682dd86
GET /v2.0/ports/{port_id}
=================  ====================================
name               iida-network-1-port-1
id                 863f2404-4a92-4991-8fab-e4312682dd86
az                 jp-east-1a
tenant_id          a5001a8b9c4a4712985c11377bd6d4fe
status             ACTIVE
admin_state_up     True
device_owner       network:router_interface
device_id          63c440e0-e082-4214-ae6e-565eba16e863
network_id         93a83e0e-424e-4e7d-8299-4bdea906354e
binding:vnic_type  normal
mac_address        fa:16:3e:ad:e9:5c
=================  ====================================

=============  ====================================
ip_address     subnet_id
=============  ====================================
192.168.0.100  38701f66-4610-493f-9c15-78f81917f362
=============  ====================================
```

ポートにdevice_ownerが設定され、 *network:router_interface* が割り当てられました。
デバイスのIDは *63c440e0-e082-4214-ae6e-565eba16e863* となっています。
これはネットワークコネクタエンドポイント**ではありません**。

マニュアルには、

> ID for internal control is displayed in device_id of port information after the port
> connected to Network Connector Endpoint.

と書かれていますので、内部の制御ポートのことのようです。


### k5-disconnect-network-connector-endpoint.py

コネクタエンドポイントとポートの接続を解消します。

> 注意！
>
> 実行するとポートそのものが削除されてしまいます！

- PUT /v2.0/network_connector_endpoints/{network connector endpoint id}/disconnect
- Disconnect Network Connector Endpoint
- ネットワークコネクタエンドポイントからインターフェイスを接続解除する


```
bash-4.4$ ./k5-disconnect-network-connector-endpoint.py
status_code: 200
{'interface': {'port_id': '863f2404-4a92-4991-8fab-e4312682dd86'}}
```



