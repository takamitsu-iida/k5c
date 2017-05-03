# k5c

K5のREST APIを利用するPythonスクリプトの例です。

Pythonは3を想定しています。

認証トークンを気にすることなく使えます。
スクリプト実行時に有効なトークンがキャッシュされてなければ勝手に取りにいきます。


## 依存モジュール

 - requests
 - tabulate

lib/site-packagesにこれらを含めていますので、インストールは不要です。


## 事前に必要な情報

- ユーザ名
- パスワード
- ドメイン名(契約番号と同じ)
- プロジェクトID(32桁英数字)
- グループ内のドメインID(32桁英数字)
- リージョン名(例：jp-east-1)

この他、必要に応じてプロキシサーバの情報が必要です。


## 使い方

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
=================  ====================================  ==========  ================================  ========
name               id                                    az          tenant_id                         status
=================  ====================================  ==========  ================================  ========
iida-test-network  2f96d845-fbe8-4c3d-9502-de39f0e03f5d  jp-east-1b  a5001a8b9c4a4712985c11377bd6d4fe  ACTIVE
=================  ====================================  ==========  ================================  ========
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

