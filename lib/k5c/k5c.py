#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
K5のREST APIへの接続機能を提供します。
依存外部モジュール
  requests
"""

import functools  # デコレータを作るのに必要
import json
import logging

logging.basicConfig(level=logging.INFO)

try:
  import requests
  # HTTPSを使用した場合に、証明書関連の警告を無視する
  requests.packages.urllib3.disable_warnings()
except ImportError:
  logging.error("requestsモジュールのインポートに失敗しました。")
  exit()

try:
  from .k5tokenmanager import k5tokenmanager
except ImportError:
  logging.error("k5tokenmanagerモジュールのインポートに失敗しました。")
  exit()

try:
  from . import k5config  # need info in k5config.py
except ImportError:
  logging.error("k5configモジュールの読み込みに失敗しました。")
  exit()


class Client(object):
  """
  トークンを気にせずにREST APIに接続する機能を提供します。
  """
  # pylint: disable=too-many-instance-attributes

  def __init__(self):
    """コンストラクタ"""
    self._timeout = k5config.TIMEOUT
    self._username = k5config.USERNAME
    self._password = k5config.PASSWORD
    self._proxies = k5config.PROXIES
    self._url_token = k5config.URL_TOKEN
    self._domain_name = k5config.DOMAIN_NAME
    self._project_id = k5config.PROJECT_ID

  def getToken(self):
    """スレッドセーフなトークン取得"""
    k5tokenmanager.lock()
    token = self._getToken()
    k5tokenmanager.release()
    return token

  def _getToken(self):
    """トークンを取得する処理"""
    # トークンマネージャが有効なキャッシュを持っていればそれを返す
    token = k5tokenmanager.token()
    if token:
      return token

    # 有効なキャッシュはなかった
    logging.info("trying to get new token from api endpoint")

    # ヘッダ情報
    headers = {
      'Accept': "application/json",
      'Content-Type': "application/json"
    }

    # 認証情報
    auth_data = {
      'auth': {
        'identity': {
          'methods': ["password"],
          'password': {
            'user': {
              'domain': {
                'name': self._domain_name
              },
              'name': self._username,
              'password': self._password
            }
          }
        },
        'scope': {
          'project': {
            'id': self._project_id
          }
        }
      }
    }
    auth_json = json.dumps(auth_data)

    # POSTを発行
    # この処理は最長でself._timeout秒かかる
    try:
      r = requests.post(self._url_token, timeout=self._timeout, proxies=self._proxies, headers=headers, data=auth_json, verify=True)
    except requests.exceptions.RequestException as e:
      logging.error(e)
      return None

    # 応答をチェック
    if not r.ok:
      return None

    # トークンはHTTPヘッダに格納されているので、それを取り出す
    token = r.headers.get('X-Subject-Token', None)
    if not token:
      return None

    # JSON形式のコンテンツを期待
    j = r.json()
    if not j:
      return None
    # print(json.dumps(j, indent=2))

    # "expires_at": "2017-05-02T08:17:12.899956Z",
    expires_at = j.get('token', {}).get('expires_at', None)

    # "issued_at": "2017-05-02T05:17:12.899983Z",
    issued_at = j.get('token', {}).get('issued_at', None)

    # 戻り値となるオブジェクトをあらためて作り直す
    result = {
      'X-Subject-Token': token,
      'expires_at': expires_at,
      'issued_at': issued_at
    }

    # 保管する
    k5tokenmanager.token(result)

    return result
  #

  # デコレータ定義
  def set_token():
    """GET/POST/PUT/DELETEの前後処理をするデコレータ"""
    def _outer_wrapper(wrapped_function):
      @functools.wraps(wrapped_function)
      def _wrapper(self, *args, **kwargs):
        #
        # 前処理
        #

        # 戻り値は必ずオブジェクトを返す
        result = {}

        # トークンを取得
        token = self.getToken()
        if not token:
          logging.error("failed to get token to access rest api")
          result['status_code'] = -100
          result['data'] = None
          return result

        # ヘッダにトークンを挿入
        headers = {
          'Accept': "application/json, text/plain",
          'Content-Type': "application/json",
          'X-Auth-Token': token.get('X-Subject-Token', '')
        }

        # タイムアウト値
        timeout = self.timeout()

        # プロキシ設定
        proxies = self.proxies()

        #
        # 実処理
        #
        r = wrapped_function(self, *args, headers=headers, timeout=timeout, proxies=proxies, verify=True, **kwargs)

        #
        # 後処理
        #

        if r is None:
          logging.error("failed to access rest api")
          result['status_code'] = -1
          result['data'] = None
          return result

        # トークンを保存
        if r.ok:
          k5tokenmanager.token(token)

        # status_codeを保存
        result['status_code'] = r.status_code

        # Content-Typeを保存
        ctype = r.headers.get('Content-Type', '')
        result['Content-Type'] = ctype

        # データを保存
        # JSON形式 or テキスト形式
        if ctype.find("json") >= 0:
          result['data'] = r.json()
        else:
          result['data'] = r.text

        return result
        #
      return _wrapper
    return _outer_wrapper
  #


  # デコレータ版のGET
  # requestsが必要とする引数はデコレータが**kwargsにセットしてくれる
  # この関数の戻り値はデコレータに横取りされ、加工されたものがコール元に返却される
  @set_token()
  def get(self, url='', params='', **kwargs):
    """指定したURLにrequests.getで接続して、レスポンスを返します。"""
    if not url:
      return None

    logging.info("GET '%s'", url)
    try:
      return requests.get(url, params=params, **kwargs)
    except requests.exceptions.RequestException as e:
      logging.error(e)
    return None


  @set_token()
  def post(self, url='', data='', **kwargs):
    """指定したURLにrequests.postで接続して、レスポンスを返します。"""
    if not url:
      return None

    logging.info("POST '%s'", url)
    try:
      return requests.post(url, json.dumps(data), **kwargs)
    except requests.exceptions.RequestException as e:
      logging.error(e)
    return None


  @set_token()
  def put(self, url='', data='', **kwargs):
    """指定したURLにrequests.putで接続して、レスポンスを返します。"""
    if not url:
      return None

    logging.info("PUT '%s'", url)
    try:
      return requests.put(url, json.dumps(data), **kwargs)
    except requests.exceptions.RequestException as e:
      logging.error(e)
    return None


  @set_token()
  def delete(self, url='', **kwargs):
    """指定したURLにrequests.deleteで接続して、レスポンスを返します。"""
    if not url:
      return None

    logging.info("DELETE '%s'", url)
    try:
      return requests.delete(url, **kwargs)
    except requests.exceptions.RequestException as e:
      logging.error(e)
    return None

  #
  # 以下、getterとsetter
  #

  def username(self, *_):
    """接続ユーザ名を取得、設定します"""
    if not _:
      return self._username
    else:
      self._username = _[0]
      return self

  def password(self, *_):
    """接続パスワードを取得、設定します"""
    if not _:
      return self._password
    else:
      self._password = _[0]
      return self

  def timeout(self, *_):
    """タイムアウト値（秒）を取得、設定します"""
    if not _:
      return self._timeout
    else:
      self._timeout = _[0]
      return self

  def proxies(self, *_):
    """プロキシ設定を取得、設定します。"""
    if not _:
      return self._proxies
    else:
      self._proxies = _[0]
      return self
  #
