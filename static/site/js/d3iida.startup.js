/* global d3, d3iida */

// d3iida.startup.js
// グローバルに名前空間'd3iida'を定義する
(function() {
  // このthisはグローバル空間
  this.d3iida = this.d3iida || (function() {
    // ユーティリティ関数を作る場合には、d3iida.utils配下にぶら下げる
    var utils = {};

    // アプリのデータを取り込む場合、appdata配下にぶら下げる
    var appdata = {};

    // ヒアドキュメント経由で静的データを取り込む場合、テキストデータをheredoc配下にぶら下げる
    var heredoc = {};

    // 地図データを取り込む場合、geodata配下にぶら下げる
    var geodata = {};

    // 公開するオブジェクト
    return {
      utils: utils,
      appdata: appdata,
      heredoc: heredoc,
      geodata: geodata
    };
  })();
  //
})();

// ユーティリティ関数を定義する
(function() {
  // x軸向きのデータの数がいくつあるのかを調べる
  d3iida.utils.calcTicksX = function(numTicks, data) {
    var numValues = 1;
    var i;
    for (i = 0; i < data.length; i++) {
      var stream_len = data[i] && data[i].values ? data[i].values.length : 0;
      numValues = stream_len > numValues ? stream_len : numValues;
    }
    numTicks = numTicks > numValues ? numTicks = numValues - 1 : numTicks;
    numTicks = numTicks < 1 ? 1 : numTicks;
    numTicks = Math.floor(numTicks);
    return numTicks;
  };

  // リサイズ用のハンドラ登録関数
  // 使い方
  // var clearFn = d3iida.utils.windowResize(chart.update);
  d3iida.utils.windowResize = function(handler) {
    if (window.addEventListener) {
      window.addEventListener('resize', handler);
    } else {
      console.warn('Failed to bind to window.resize with: ', handler);
    }
    // イベントハンドラを削除する関数を返却する
    return function() {
      window.removeEventListener('resize', handler);
    };
  };

  // テスト用にランダムな値を作成する
  d3iida.utils.rndNum = function(min, max) {
    var mi = min || 100;
    var ma = max || 500;
    var rnd = ~~(Math.random() * ma);
    rnd = rnd < mi ? mi : rnd;
    return rnd;
  };

  // テスト用にランダムな値の配列を作成する
  d3iida.utils.rndNumbers = function(len, max) {
    var l = len || 50;
    var m = max || 100;
    // ランダム値をランダム個作成する。この方法が高速らしい。
    var nums = d3.range(~~(Math.random() * l)).map(function(d, i) {
      return ~~(Math.random() * m);
    });
    return nums;
  };
  //
})();

// モジュール化の動作確認
// helloモジュール
(function() {
  d3iida.hello = function module() {
    // プライベート変数
    // クロージャで外から設定できるようにする
    var fontSize = 10;
    var fontColor = 'red';

    // 外部にイベントを公開できるようにするためにd3.dispatchを使う。
    // イベント名は任意でよく、ここではcustomHoverにする
    // イベントは何個でも並べられる
    var dispatch = d3.dispatch('customHover', 'anyEvent');

    // d3でデータを紐付けしたあとcall()することでこれが呼ばれる
    function exports(_selection) {
      _selection.each(function(_data) {
        // _dataは紐付けしたデータそのもの。配列全体。
        d3.select(this)
          .append('div')
          .style('font-size', fontSize + 'px')
          .style('color', fontColor)
          .html('helloモジュールに渡されたデータ = ' + _data)
          .on('mouseover', function() {
            // カスタムイベントをディスパッチする
            dispatch.call('customHover', this, _data);
          });
      });
    }

    // クロージャ定義

    // fontSize(10)
    exports.fontSize = function(_x) {
      if (!arguments.length) {
        return fontSize;
      }
      fontSize = _x;
      return this;
    };

    // fontColor('red')
    exports.fontColor = function(_x) {
      if (!arguments.length) {
        return fontColor;
      }
      fontColor = _x;
      return this;
    };

    // カスタムイベントを'on'で発火できるようにリバインドする
    // v3までのやり方
    // d3.rebind(exports, dispatch, 'on');
    // v4のやり方
    exports.on = function() {
      var value = dispatch.on.apply(dispatch, arguments);
      return value === dispatch ? exports : value;
    };

    // 呼び出し元にはexportsを返却する。
    return exports;
  };

  // 使い方
  d3iida.hello.example = function() {
    // データセット
    var dataset = [10, 20, 30, 40, 50];

    // hello()モジュールをインスタンス化
    var hello = d3iida.hello().fontSize('20').fontColor('green');

    // カスタムイベントにハンドラを登録する
    hello.on('customHover', function(d) {
      d3.select('#message').append('p').text('customHoverイベント: ' + d);
    });

    // セレクションにデータを紐付けてcall()する
    d3.select('#hello').datum(dataset).call(hello);
  };
  //
})();
