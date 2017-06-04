#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
K5のREST APIへの接続機能を提供します。

依存外部モジュール
  requests
"""

try:
  import configparser  # python3
except ImportError:
  import ConfigParser as configparser  # python2
import functools  # デコレータを作るのに必要
import json
import logging
import os
import sys


# アプリケーションのホームディレクトリ
if getattr(sys, 'frozen', False):
  # cx_Freezeで固めた場合は実行ファイルからの相対
  app_home = os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))
else:
  # このファイルからの相対
  app_home = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# 自身の名前から拡張子を除いてプログラム名を得る
app_name = os.path.splitext(os.path.basename(__file__))[0]

# 設定ファイルのパス
# $app_home/conf/k5config.ini
config_file = os.path.join(app_home, "conf", "k5config.ini")
if not os.path.exists(config_file):
  logging.error("File not found %s : ", config_file)
  sys.exit(1)

# 設定ファイルを読む
try:
  cp = configparser.SafeConfigParser()
  cp.read(config_file, encoding='utf8')

  # [k5] セクション
  config = cp['k5']
  DOMAIN_NAME = config['DOMAIN_NAME']
  DOMAIN_ID = config['DOMAIN_ID']
  PROJECT_ID = config['PROJECT_ID']
  TENANT_ID = config['PROJECT_ID']
  REGION = config['REGION']
  USERNAME = config['USERNAME']
  PASSWORD = config['PASSWORD']
  AZ = config['AZ']

  # エンドポイント(APIマニュアルを見ないと、どのエンドポイントを利用すべきか分からない)
  EP_TOKEN = "https://identity." + REGION + ".cloud.global.fujitsu.com"
  EP_IDENTITY = "https://identity." + REGION + ".cloud.global.fujitsu.com"
  EP_NETWORK = "https://networking." + REGION + ".cloud.global.fujitsu.com"
  EP_ELB = "https://loadbalancing." + REGION + ".cloud.global.fujitsu.com"
  EP_CEILOMETER = "https://telemetry." + REGION + ".cloud.global.fujitsu.com"

  # [proxy] セクション
  config = cp['proxy']
  USE_PROXY = config.getboolean('USE_PROXY')
  if USE_PROXY:
    PROXIES = {
      'http': config['HTTP_PROXY'],
      'https': config['HTTP_PROXY']
    }
  else:
    PROXIES = None

  # [requests] セクション
  config = cp['requests']
  TIMEOUT = config.getint('TIMEOUT')

  # [k5c] セクション
  config = cp['k5c']
  USE_FILE_HANDLER = config.getboolean('USE_FILE_HANDLER')

except configparser.Error as e:
  logging.error("k5config.iniの読み込みに失敗しました。")
  logging.exception(e)
  sys.exit(1)

try:
  from .k5tokenmanager import k5tokenmanager
except ImportError as e:
  logging.error("k5tokenmanagerモジュールのインポートに失敗しました。")
  logging.exception(e)
  sys.exit(1)

#
# ログ設定
#

# ログファイルの名前
log_file = app_name + ".log"

# ログファイルを置くディレクトリ
log_dir = os.path.join(app_home, "log")
if not os.path.isdir(log_dir):
  try:
    os.makedirs(log_dir)
  except OSError:
    pass

# ロギングの設定
# レベルはこの順で下にいくほど詳細になる
#   logging.CRITICAL
#   logging.ERROR
#   logging.WARNING --- 初期値はこのレベル
#   logging.INFO
#   logging.DEBUG
#
# ログの出力方法
# logger.debug("debugレベルのログメッセージ")
# logger.info("infoレベルのログメッセージ")
# logger.warning("warningレベルのログメッセージ")

# ロガーを取得
logger = logging.getLogger(__package__)

# ログレベル設定
logger.setLevel(logging.INFO)

# フォーマット
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 標準出力へのハンドラ
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.WARNING)
logger.addHandler(stdout_handler)

# ログファイルのハンドラ
if USE_FILE_HANDLER:
  file_handler = logging.FileHandler(os.path.join(log_dir, log_file), 'a+')
  file_handler.setFormatter(formatter)
  file_handler.setLevel(logging.INFO)
  logger.addHandler(file_handler)

try:
  import requests
  # HTTPSを使用した場合に、証明書関連の警告を無視する
  requests.packages.urllib3.disable_warnings()
except ImportError as e:
  logging.error("requestsモジュールのインポートに失敗しました。")
  logging.exception(e)
  sys.exit(1)


class Client(object):
  """
  トークンを気にせずにREST APIに接続する機能を提供します。
  """
  # pylint: disable=too-many-instance-attributes

  def __init__(self):
    """コンストラクタ"""
    self._timeout = TIMEOUT
    self._username = USERNAME
    self._password = PASSWORD
    self._proxies = PROXIES
    self._url_token = EP_TOKEN + "/v3/auth/tokens"
    self._domain_name = DOMAIN_NAME
    self._project_id = PROJECT_ID

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
    logger.info("trying to get new token from api endpoint")

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
    r = None
    try:
      r = requests.post(self._url_token, timeout=self._timeout, proxies=self._proxies, headers=headers, data=auth_json, verify=True)
    except requests.exceptions.ConnectionError:
      logger.error("requests.exceptions.ConnectionError occured")
    except requests.exceptions.HTTPError:
      logger.error("requests.exceptions.HTTPError occured")
    except requests.exceptions.SSLError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ProxyError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ReadTimeout:
      logger.error("requests.exceptions.ReadTimeout occured")
    except requests.exceptions.RequestException as e:
      logger.exception(e)

    # 応答をチェック
    if not r or not r.ok:
      return None

    # トークンはHTTPヘッダに格納されているので、それを取り出す
    token = r.headers.get('X-Subject-Token', None)
    if not token:
      return None

    logger.info("get new token, %s", token)

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
          logger.error("failed to get token to access rest api")
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
          result['status_code'] = -1
          result['data'] = None
          return result

        # ログ
        logger.info("%s '%s'", r.status_code, r.url)

        # トークンを保存
        if r.ok:
          k5tokenmanager.token(token)
        elif r.status_code == 401:
          k5tokenmanager.token(None)

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

    logger.info("GET '%s'", url)
    try:
      return requests.get(url, params=params, **kwargs)
    except requests.exceptions.ConnectionError:
      logger.error("requests.exceptions.ConnectionError occured")
    except requests.exceptions.HTTPError:
      logger.error("requests.exceptions.HTTPError occured")
    except requests.exceptions.SSLError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ProxyError:
      logger.error("requests.exceptions.ProxyError occured")
    except requests.exceptions.ReadTimeout:
      logger.error("requests.exceptions.ReadTimeout occured")
    except requests.exceptions.RequestException as e:
      logger.exception(e)
    return None


  @set_token()
  def post(self, url='', data='', **kwargs):
    """指定したURLにrequests.postで接続して、レスポンスを返します。"""
    if not url:
      return None

    logger.info("POST '%s'", url)
    try:
      return requests.post(url, json.dumps(data), **kwargs)
    except requests.exceptions.ConnectionError:
      logger.error("requests.exceptions.ConnectionError occured")
    except requests.exceptions.HTTPError:
      logger.error("requests.exceptions.HTTPError occured")
    except requests.exceptions.SSLError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ProxyError:
      logger.error("requests.exceptions.ProxyError occured")
    except requests.exceptions.ReadTimeout:
      logger.error("requests.exceptions.ReadTimeout occured")
    except requests.exceptions.RequestException as e:
      logger.exception(e)
    return None


  @set_token()
  def put(self, url='', data='', **kwargs):
    """指定したURLにrequests.putで接続して、レスポンスを返します。"""
    if not url:
      return None

    logger.info("PUT '%s'", url)
    try:
      return requests.put(url, json.dumps(data), **kwargs)
    except requests.exceptions.ConnectionError:
      logger.error("requests.exceptions.ConnectionError occured")
    except requests.exceptions.HTTPError:
      logger.error("requests.exceptions.HTTPError occured")
    except requests.exceptions.SSLError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ProxyError:
      logger.error("requests.exceptions.ProxyError occured")
    except requests.exceptions.ReadTimeout:
      logger.error("requests.exceptions.ReadTimeout occured")
    except requests.exceptions.RequestException as e:
      logger.exception(e)
    return None


  @set_token()
  def delete(self, url='', **kwargs):
    """指定したURLにrequests.deleteで接続して、レスポンスを返します。"""
    if not url:
      return None

    logger.info("DELETE '%s'", url)
    try:
      return requests.delete(url, **kwargs)
    except requests.exceptions.ConnectionError:
      logger.error("requests.exceptions.ConnectionError occured")
    except requests.exceptions.HTTPError:
      logger.error("requests.exceptions.HTTPError occured")
    except requests.exceptions.SSLError:
      logger.error("requests.exceptions.SSLError occured")
    except requests.exceptions.ProxyError:
      logger.error("requests.exceptions.ProxyError occured")
    except requests.exceptions.ReadTimeout:
      logger.error("requests.exceptions.ReadTimeout occured")
    except requests.exceptions.RequestException as e:
      logger.exception(e)
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
