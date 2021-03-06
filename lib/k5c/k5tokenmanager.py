#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""K5 REST APIに必要なトークンをスレッドセーフに管理するためのモジュールです."""

import datetime
import logging
import os
import pickle
import sys
from threading import RLock

# ロガー
logger = logging.getLogger(__package__)


class K5TokenManager(object):
  """接続状態を管理します"""
  #
  # 想定しているトークンオブジェクトの形式
  # getToken()の戻り値
  # {
  #    'X-Subject-Token': 'ed0456b9f91041e88db9163e7cf88043',
  #    'expires_at': '2017-05-02T09:11:58.198526Z',
  #    'issued_at': '2017-05-02T06:11:58.198552Z'
  # }
  #

  # 時刻表示のフォーマットはISO 8601形式
  # Tはセパレータ、ZはZuluの略でUTCを意味する
  DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

  # アプリケーションのホームディレクトリ
  if getattr(sys, 'frozen', False):
    # cx_Freezeで固めた場合は実行ファイルからの相対
    app_home = os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))
  else:
    # このファイルからの相対
    app_home = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

  # データを置くディレクトリ
  data_dir = os.path.join(app_home, "data")
  if not os.path.isdir(data_dir):
    try:
      os.makedirs(data_dir)
    except OSError:
      pass

  # トークンを保存するファイル名(中身はjsonではなくpickle形式)
  TOKEN_FILENAME = "k5-token.pickle"

  # トークンファイルへのパス
  token_path = os.path.join(data_dir, TOKEN_FILENAME)

  def __init__(self):
    """コンストラクタ"""

    # オンメモリのトークン
    self._token_json = None

    # 排他制御用のロック
    self._lock = RLock()

  def saveToken(self, token):
    """トークンをpickleでファイルに保存します"""
    try:
      with open(self.token_path, 'wb') as f:
        pickle.dump(token, f)
    except IOError as e:
      logger.exception(e)

  def loadToken(self):
    """pickleでファイルに保存されているトークンを復元します"""
    if not os.path.isfile(self.token_path):
      return None

    try:
      with open(self.token_path, 'rb') as f:
        token = pickle.load(f)
        return token
    except IOError as e:
      logger.exception(e)
    except ValueError as e:
      logger.exception(e)
    return None

  def isNotExpired(self, token):
    """有効期限が切れていないことを確認します"""
    now = datetime.datetime.utcnow()

    # 有効期限を取り出す
    # 'expires_at': '2017-05-02T09:11:58.198526Z',
    expires_at_str = token.get('expires_at', None)

    # expires_atが存在しない場合はあらためて取得し直す
    if expires_at_str is None:
      return False

    # 時刻に戻す
    expires_at = datetime.datetime.strptime(expires_at_str, self.DATE_FORMAT)

    # dirty hack
    # 誤差と処理遅延を考えて5分を減算する
    expires_at -= datetime.timedelta(minutes=5)

    if now < expires_at:
      return True
    #
    return False

  def getCachedToken(self):
    """メモリもしくはディスクからトークンのキャッシュを取得して返します"""
    # まずはメモリキャッシュの有無を確認して、あればそれを返却
    # Webアプリケーションの時はメモリ上にキャッシュされている可能性が高い
    token = self._token_json
    if token and self.isNotExpired(token):
      logger.info("Found token on memory cache")
      return token
    # logger.info("There is no token on memory cache")

    # メモリキャッシュにない場合は、ディスクから探す
    token = self.loadToken()

    # トークンがディスクに保存されていない
    if not token:
      logger.info("There is no token on disk cache")
      return None

    # トークンの有効期間が切れてないか確認する
    if self.isNotExpired(token):
      logger.info("Found token on disk cache")
      self._token_json = token
      return token
    logger.info("There is no available token on disk cache")
    return None

  def lock(self):
    """ロックを獲得します"""
    self._lock.acquire()

  def release(self):
    """ロックを開放します."""
    self._lock.release()

  def token(self, *_):
    """トークンを取得、設定します."""
    if not _:
      return self.getCachedToken()
    else:
      self._token_json = _[0]
      self.saveToken(_[0])
      return self

###############################################################################

#
# K5TokenManagerクラスのインスタンスをグローバル名前空間に一つ生成して共有する
#
k5tokenmanager = K5TokenManager()
