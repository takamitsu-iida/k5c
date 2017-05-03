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

