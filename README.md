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

ネットワークとサブネットは1:1の関係ですが、先に作成するのはネットワークです。
サブネットを作成するときに、先に作ったネットワークのidを指定することで、どのネットワークに所属させるサブネットかを指定します。

ポートはネットワークに紐付けます。
ポートを作成するときに、ネットワークのidを指定することで、どのネットワークに所属させるか指定します。

IPアドレスはポートに付与されます。
ネットワーク内にポートは何個でも作れます。
ポートを作った後で、オーナー（仮想ルータとかコネクタエンドポイント）との紐付けを行います。

以上の関係性から、作成すべき順番はこのようになります。

1. ネットワークを作成して、ネットワークIDを調べる
2. そのネットワークIDを指定してサブネットを作成する
3. ネットワークIDをとサブネットIDを指定してポートを作成する
4. デバイス(仮想ルータやコネクタエンドポイント)とポートを紐付ける


### ネットワークコネクタ

少々ややこしいのは、データセンター構内で別ネットワークと接続する場合です。ネットワークコネクタという聞きなれない用語が登場します。

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

Availability Zoneの中にはネットワークコネクタプールというものが存在します。これは自動で作成されたもので、削除も追加もできません。

ネットワークコネクタプールの中にネットワークコネクタを作成します。これが外部との接点になります。外側の接続設定はK5事業者が行いますので、（申請書を書くとか）何らかの形で依頼をすることになると思います。

ネットワークコネクタには、コネクタエンドポイントを作成します。これが内側との接点になります。ポートのオーナーとしてコネクタエンドポイントを指定することで、内側と紐付けられます。

ネットワークコネクタには複数のコネクタエンドポイントを作成できます。したがって、一つの構内接続を複数のプロジェクトで共有することもできます。

作成する順番としては、このようになります。

1. ネットワークコネクタプールのIDを調べる
2. そのプールのIDを指定してネットワークコネクタを作成する
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


## スクリプトの実行

scriptsにサンプルスクリプトを置いています。

Windowsのコマンドプロンプトでも実行できますが、画面の横幅が狭いため見苦しい表示になってしまいます。
TeraTERMでCygwinに接続する、出力をファイルにリダイレクトしてエディタで確認する、といった工夫をするといいと思います。

K5のAPIを操作するためには、事前に認証トークンを取得しなければいけませんが、このスクリプトはトークンを気にせず使えます。
スクリプト実行時に有効なトークンがキャッシュされていればそれを使います。
トークンのキャッシュがない、あるいは有効期限が切れている場合には、REST API実行前にトークンを自動的に取りにいきます。


### k5-token.py

APIエンドポイントにアクセスできるかテストするためのスクリプトです。

```
bash-4.4$ ./k5-token.py
{
  "expires_at": "2017-05-02T13:31:28.092961Z",
  "X-Subject-Token": "f240eccd302f4a31b3ccdb4b0d1bcd7f",
  "issued_at": "2017-05-02T10:31:28.092987Z"
}
bash-4.4$
```

issued_atとexpires_atの差分が3時間ほどありますので、トークンの有効期間は3時間と考えられます。
トークンは取得するたびに変わります。
払い出せるトークンの数には制限があるかもしれませんので、
一度取得したトークンはキャッシュして使いまわすようにしています。


### k5-list-networks.py

APIリファレンス（Network編）Version 1.8

1.2.6.1 List networks

Lists networks to which the specified tenant has access.

```
bash-4.4$ ./k5-list-networks.py
GET /v2.0/networks
====================================  =================  ================================  ==========  ========
id                                    name               tenant_id                         az          status
====================================  =================  ================================  ==========  ========
375c49fa-a706-4676-b55b-2d3554e5db6a  inf_az2_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
4516097a-84dd-476f-824a-6b2fd3cc6499  inf_az2_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
852e40a7-82a3-4196-8b84-46f55d01ccba  inf_az2_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
abe76a93-87c3-4635-b0f3-40f794165c26  inf_az2_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
bfca06b3-0b23-433f-96af-4f54bf963e5f  inf_az2_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1b  ACTIVE
6d9df982-7a89-462a-8b17-8a8e5befa63e  inf_az1_ext-net03  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
92f386c1-59fe-48ca-8cf9-b95f81920466  inf_az1_ext-net02  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
a4715541-c915-444b-bed6-99aa1e8b15c9  inf_az1_ext-net04  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
af4198a9-b392-493d-80ec-a7c6e5a1c22a  inf_az1_ext-net01  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
cd4057bd-f72e-4244-a7dd-1bcb2775dd67  inf_az1_ext-net05  31ceb599e8ff48aeb66f2fd748988960  jp-east-1a  ACTIVE
====================================  =================  ================================  ==========  ========
bash-4.4$
```


### k5-create-network.py

APIリファレンス（Network編）Version 1.8

1.2.6.2 Create network

Creates a network.

注意:
 - 作成するネットワークの名前とゾーンはスクリプトのmain()で指定
 - 同じ名前であっても何個でも作れる（idで区別）


```
bash-4.4$ ./k5-create-network.py
POST /v2.0/networks
=========  ====================================
name       iida-test-network
id         acb539fc-4a5d-4fc3-bc70-324ee336d587
az         jp-east-1b
tenant_id  a5001a8b9c4a4712985c11377bd6d4fe
status     ACTIVE
=========  ====================================
bash-4.4$
```


### k5-show-network.py

APIリファレンス（Network編）Version 1.8

1.2.6.3 Show network

Shows information for a specified network.

```
bash-4.4$ ./k5-show-network.py 375c49fa-a706-4676-b55b-2d3554e5db6a
GET /v2.0/networks/{network_id}
=================  ====================================  ==========  ========
id                 name                                  az          status
=================  ====================================  ==========  ========
inf_az2_ext-net01  375c49fa-a706-4676-b55b-2d3554e5db6a  jp-east-1b  ACTIVE
=================  ====================================  ==========  ========

====================================
subnets
====================================
5079f324-5db0-44ee-92ac-3a6b7977b23f
a56b6058-0479-43a1-8b27-01c1c05e96a2
c1da3ee7-51c3-4801-bb97-aa03a4383ef0
e96e55b8-84bb-4777-a782-a5d6e8340039
f5e9ec37-88ec-494b-ac55-dae101a54cc1
====================================
bash-4.4$
```

### k5-delete-network.py

APIリファレンス（Network編）Version 1.8

1.2.6.5 Delete network

Deletes a specified network and its associated resources.

```
実行例（成功した場合は特にデータは戻りません）
bash-4.4$ ./k5-delete-network.py 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b
status_code: 204
```

```
実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-network.py 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b
status_code: 404
{'NeutronError': {'type': 'NetworkNotFound', 'detail': '', 'message': 'Network 7bc1d12f-5ef6-4177-aa87-c2a5c74aa40b could not be found'}}
bash-4.4$
```

