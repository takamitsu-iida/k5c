# K5ネットワークの構成情報を記録する

K5のネットワーク構成を変更していく場合、作業の前と後で構成がどのように変わったのか、追跡できないといけません。
また、環境を第三者から引き継いだときには、それがどいう構成になっているのか迅速に把握すべきです。

ネットワーク構成を取得するAPIがあればよいのですが、
(2017年5月時点では)そういった便利な機能は提供されていませんので、
利用者側でAPIを操作して得た情報を保全するしかありません。

List系とShow系のAPIを叩いて得られる情報を保存するスクリプトを作成しました。


> NOTE:
>
> だいたいのネットワーク機器にはshow tech-supportというコマンドがありますが、
> K5の利用者側におけるshow techみたいなものです。

<BR>

> NOTE:
>
> うっかりファイアウォールの情報を採取対象から漏らしたので、いつか追加すること（自分メモ）

<BR>

## 依存モジュール

- tinydb

`pip install tinydb` でインストールしてください。


<BR>

## 構成の保存

使い方
- bin/k5-inspect -c

保存先
- data/db.json

以下の情報を採取してデータベースに保存します。

-    List Network Connector Pools
-    List Network Connectors
-    Show Network Connector

-    List Network Connector Endpoints
-    Show Network Connector Endpoint
-    List Connected Interfaces of Network Connector Endpoint


-    List networks
-    Show network

-    List subnets
-    Show subnet

-    List ports
-    Show port

-    List routers
-    Show router

-    List floating IPs
-    Show floating IP details


> NOTE:
>
> いまの作りでは実行するたびにデータベースに追記してしまいますので、実行前にdb.jsonを削除するか、名前を変更してください。
> 名前を付けて保存しておけば『その時点ではこうなっていた』という貴重な証拠になるでしょう。

<BR>


## 構成のダンプ表示

使い方
- bin/k5-inspect -d

実行例

このようなダンプが得られます。
作業前のダンプと作業後のダンプでdiffをとるといいでしょう。

```
bash-4.4$ ./bin/k5-inspect.py -d
[
  {
    "network_connector_pools": [
      {
        "name": "jp-east-1a_connector_pool_01",
        "id": "e0a80446-203e-4b28-abec-d4b031d5b63e"
      }
    ]
  },
  {
    "network_connectors": [
      {
        "network_connector_pool_id": "e0a80446-203e-4b28-abec-d4b031d5b63e",
        "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
        "network_connector_endpoints": [
          "848a40c2-7ded-4df8-a43d-e55b912811a2"
        ],
        "name": "iida-az1-nc",
        "id": "88f343e8-a956-4bcc-853f-3c40d53cbb49"
      }
    ]
  },
```

<BR>

## ルータ情報のインスペクト

使い方
- bin/k5-inspect -r

ルータにどのポートが繋がっているのか、ルータがもっている経路情報は何か、等を人間にわかりやすい形で表示します。

実行例

```
bash-4.4$ ./bin/k5-inspect.py -r
Router iida-az1-router01 is ACTIVE, Admin state is True
  UUID is ffbd70be-24cf-4dff-a4f6-661bf892e313
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1a
  External gateway network is cd4057bd-f72e-4244-a7dd-1bcb2775dd67 ,snat is True
  Routing table
    10.0.0.0/8 via 10.1.2.9
    172.16.0.0/12 via 10.1.2.9
    192.168.0.0/16 via 10.1.2.9
  Port iida-az1-net01-port01 is ACTIVE, Admin state is True
    Port uuid is 689d24c7-02a2-4dfd-b809-9ad4060e079f
    binding:vnic_type is normal
    Hardware address is fa:16:3e:84:72:35
    Internet address is 10.1.1.1 ,Subnet is abbbbcf4-ea8f-4218-bbe7-669231eeba30
  Port iida-az1-net02-port01 is ACTIVE, Admin state is True
    Port uuid is bdab1ca6-fd32-4729-9e97-3827b72d7bc5
    binding:vnic_type is normal
    Hardware address is fa:16:3e:ea:73:57
    Internet address is 10.1.2.1 ,Subnet is 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6

Router iida-az2-router01 is ACTIVE, Admin state is True
  UUID is c97f9aa5-eacc-48ae-b5df-82784bce8b63
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1b
  External gateway network is 4516097a-84dd-476f-824a-6b2fd3cc6499 ,snat is True
  Routing table
    No route is set.
  Port iida-az2-net01-port01 is ACTIVE, Admin state is True
    Port uuid is 59114983-8715-4dc7-879d-afbf69ef19a7
    binding:vnic_type is normal
    Hardware address is fa:16:3e:d3:8f:b4
    Internet address is 10.2.1.1 ,Subnet is 07041634-9f01-4518-a2c8-1e6ea8d956ee
  Port iida-az2-net02-port01 is ACTIVE, Admin state is True
    Port uuid is c0b78abd-39fb-4833-97b0-8050d93b9cd5
    binding:vnic_type is normal
    Hardware address is fa:16:3e:32:cd:44
    Internet address is 10.2.2.1 ,Subnet is 50bf50fa-816b-4e7e-98da-8379d9675101

bash-4.4$
```

<BR>

## ネットワーク情報のインスペクト

使い方
- bin/k5-inspect -n

ネットワークに対応付けられているサブネットの情報、ネットワークに付随するポートの情報を人間に分かりやすく表示します。

実行例

```
bash-4.4$ ./bin/k5-inspect.py -n
Network iida-az1-net01 is ACTIVE, Admin state is True
  UUID is 8f15da62-c7e5-47ec-8668-ee502f6d00d2
  External is False
  Shared is False
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1a
  Subnet iida-az1-subnet01 is abbbbcf4-ea8f-4218-bbe7-669231eeba30
    Internet address is 10.1.1.0/24
    Gateway is 10.1.1.1
    DHCP is True
    DNS nameserver is not set.
    Host routes is not set.
  Port in this network
  Port iida-az1-net01-port01 is ACTIVE, Admin state is True
    Port uuid is 689d24c7-02a2-4dfd-b809-9ad4060e079f
    binding:vnic_type is normal
    Hardware address is fa:16:3e:84:72:35
    Internet address is 10.1.1.1 ,Subnet is abbbbcf4-ea8f-4218-bbe7-669231eeba30

Network iida-az1-net02 is ACTIVE, Admin state is True
  UUID is e3c166c0-7e90-4c6e-857e-87fd985f98ac
  External is False
  Shared is False
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1a
  Subnet iida-az1-subnet02 is 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
    Internet address is 10.1.2.0/24
    Gateway is 10.1.2.1
    DHCP is True
    DNS nameservers
      133.162.193.10
      133.162.193.9
    Host routes
      10.0.0.0/8 via 10.1.2.9
      10.1.1.0/24 via 10.1.2.1
      172.16.0.0/12 via 10.1.2.9
      192.168.0.0/16 via 10.1.2.9
  Port in this network
  Port iida-az1-net02-port02 is ACTIVE, Admin state is True
    Port uuid is 74233502-90d1-47f7-976e-f3def361d2a1
    binding:vnic_type is normal
    Hardware address is fa:16:3e:2a:5a:58
    Internet address is 10.1.2.9 ,Subnet is 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6
  Port iida-az1-net02-port01 is ACTIVE, Admin state is True
    Port uuid is bdab1ca6-fd32-4729-9e97-3827b72d7bc5
    binding:vnic_type is normal
    Hardware address is fa:16:3e:ea:73:57
    Internet address is 10.1.2.1 ,Subnet is 2093ac3c-45c6-4fdf-bb9d-7dfa742c47f6

Network iida-az2-net01 is ACTIVE, Admin state is True
  UUID is 0cbf1e4d-479b-4336-8ba9-eb530fe55adb
  External is False
  Shared is False
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1b
  Subnet iida-az2-subnet01 is 07041634-9f01-4518-a2c8-1e6ea8d956ee
    Internet address is 10.2.1.0/24
    Gateway is 10.2.1.1
    DHCP is True
    DNS nameserver is not set.
    Host routes is not set.
  Port in this network
  Port iida-az2-net01-port01 is ACTIVE, Admin state is True
    Port uuid is 59114983-8715-4dc7-879d-afbf69ef19a7
    binding:vnic_type is normal
    Hardware address is fa:16:3e:d3:8f:b4
    Internet address is 10.2.1.1 ,Subnet is 07041634-9f01-4518-a2c8-1e6ea8d956ee
  Port  is ACTIVE, Admin state is True
    Port uuid is f413e79a-1747-4256-9b7f-483879218e1c
    binding:vnic_type is normal
    Hardware address is fa:16:3e:8d:ba:9f
    Internet address is 10.2.1.3 ,Subnet is 07041634-9f01-4518-a2c8-1e6ea8d956ee

Network iida-az2-net02 is ACTIVE, Admin state is True
  UUID is 8b004a16-c5a2-4e1d-ab9e-a417fef45ec7
  External is False
  Shared is False
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Availability zone is jp-east-1b
  Subnet iida-az2-subnet02 is 50bf50fa-816b-4e7e-98da-8379d9675101
    Internet address is 10.2.2.0/24
    Gateway is 10.2.2.1
    DHCP is True
    DNS nameserver is not set.
    Host routes is not set.
  Port in this network
  Port iida-az2-net02-port02 is DOWN, Admin state is True
    Port uuid is 02f29c2b-8a16-4be5-a15e-e943f02fe2f9
    binding:vnic_type is normal
    Hardware address is fa:16:3e:01:27:e7
    Internet address is 10.2.2.9 ,Subnet is 50bf50fa-816b-4e7e-98da-8379d9675101
  Port  is ACTIVE, Admin state is True
    Port uuid is 7e3bd7f0-f2ba-4bd3-bcc5-69111429a98b
    binding:vnic_type is normal
    Hardware address is fa:16:3e:e7:43:73
    Internet address is 10.2.2.2 ,Subnet is 50bf50fa-816b-4e7e-98da-8379d9675101
  Port iida-az2-net02-port01 is ACTIVE, Admin state is True
    Port uuid is c0b78abd-39fb-4833-97b0-8050d93b9cd5
    binding:vnic_type is normal
    Hardware address is fa:16:3e:32:cd:44
    Internet address is 10.2.2.1 ,Subnet is 50bf50fa-816b-4e7e-98da-8379d9675101

bash-4.4$
```


<BR>

## ネットワークコネクタ情報のインスペクト

使い方
- bin/k5-inspect -nc

ネットワークコネクタに対応付けられているコネクタエンドポイントの情報を人間に分かりやすく表示します。

実行例

```
bash-4.4$ ./bin/k5-inspect.py -nc
Network Connector iida-az1-nc
  UUID is 88f343e8-a956-4bcc-853f-3c40d53cbb49
  Pool uuid is e0a80446-203e-4b28-abec-d4b031d5b63e
  Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
  Network Connector Endpoint iida-az1-ncep
    Ncep uuid is 848a40c2-7ded-4df8-a43d-e55b912811a2
    Type is availability_zone
    Tenant uuid is a5001a8b9c4a4712985c11377bd6d4fe
    Location is jp-east-1a
```

