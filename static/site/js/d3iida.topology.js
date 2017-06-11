/* global d3, d3iida */

// 2017.06.01
// Takamitsu IIDA

(function() {
  d3iida.topologyChart = function module() {
    // SVGの枠の大きさ
    var width = 600;
    var height = 400;

    // 'g'の描画領域となるデフォルトのマージン
    var margin = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 40
    };

    // チャート描画領域のサイズw, h
    // 軸や凡例がはみ出てしまうので、マージンの分だけ小さくしておく。
    var w = width - margin.left - margin.right;
    var h = height - margin.top - margin.bottom;

    // ダミーデータ
    var dummy = ['dummy'];

    // カスタムイベントを登録する
    var dispatch = d3.dispatch('customHover');

    // 描画領域の大きさに変更はあるか
    var sizeChanged = false;

    // 色
    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulation = d3.forceSimulation()
      .force('link', d3.forceLink().id(function(d) {
        return d.id;
      }))
      .force('charge', d3.forceManyBody())
      .force('collide', d3.forceCollide(function(d) {
        return 20;
      }).iterations(16))
      .force('center', d3.forceCenter(w / 2, h / 2))
      .force('y', d3.forceY(0))
      .force('x', d3.forceX(0));

    // call()されたときに呼ばれる公開関数
    function exports(_selection) {
      _selection.each(function(_data) {
        if (!_data) {
          // データにnullを指定してcall()した場合は、既存のSVGを削除する
          d3.select(this).select('svg').remove();
          return;
        }

        var dataNodes = _data.nodes;
        var dataLinks = _data.links;

        // ダミーデータを紐付けることでsvgの重複作成を防止する
        var svgAll = d3.select(this).selectAll('svg').data(dummy);

        svgAll
          // ENTER領域
          .enter()
          .append('svg')
          .attr('debug', function() {
            console.log('new svg created');
          })
          // ENTER + UPDATE領域に対して設定すれば楽だけど、毎回変更するのは重たい
          // .merge(svgAll)
          .attr('width', width)
          .attr('height', height);

        // 実際に描画領域の大きさに変更がある場合だけUPDATE領域を変更する
        if (sizeChanged) {
          svgAll
            .attr('width', width)
            .attr('height', height);
        }

        // チャート描画領域'g'を追加
        var topologyChartAll = d3.select(this).select('svg').selectAll('.topologyChart').data(dummy);
        topologyChartAll
          // ENTER領域
          .enter()
          .append('g')
          .classed('topologyChart', true)
          .attr('width', w)
          .attr('height', h)
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        if (sizeChanged) {
          topologyChartAll
            .attr('width', w)
            .attr('height', h)
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
        }

        // 作成済みの描画領域'g'を選択しておく
        var topologyChart = d3.select(this).select('.topologyChart');

        var link = topologyChart
          .append('g')
          .attr('class', 'links')
          .selectAll('line')
          .data(dataLinks)
          .enter()
          .append('line')
          .attr('stroke', 'black');

        var node = topologyChart
          .append('g')
          .attr('class', 'nodes')
          .selectAll('circle')
          .data(dataNodes)
          .enter()
          .append('circle')
          .attr('r', function(d) {
            if (d.node_type === 'PORT') {
              return 4;
            } else if (d.node_type === 'ROUTER') {
              return 10;
            } else if (d.node_type === 'NETWORK') {
              return 15;
            } else if (d.node_type === 'NC') {
              return 8;
            } else if (d.node_type === 'NCEP') {
              return 6;
            }
            return 3;
          })
          .attr('fill', function(d) {
            if (d.node_type === 'PORT') {
              return color(1);
            } else if (d.node_type === 'ROUTER') {
              return color(2);
            } else if (d.node_type === 'NETWORK') {
              return color(3);
            } else if (d.node_type === 'NC') {
              return color(4);
            } else if (d.node_type === 'NCEP') {
              return color(5);
            }
            return color(6);
          })
          .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

        var ticked = function() {
          link
            .attr('x1', function(d) {
              return d.source.x;
            })
            .attr('y1', function(d) {
              return d.source.y;
            })
            .attr('x2', function(d) {
              return d.target.x;
            })
            .attr('y2', function(d) {
              return d.target.y;
            });

          node
            .attr('cx', function(d) {
              return d.x;
            })
            .attr('cy', function(d) {
              return d.y;
            });
        };

        simulation
          .nodes(dataNodes)
          .on('tick', ticked);

        simulation.force('link')
          .links(dataLinks);

        sizeChanged = false;
        //
      });
    }

    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    exports.width = function(_) {
      if (!arguments.length) {
        return width;
      }
      width = _;
      w = width - margin.left - margin.right;
      sizeChanged = true;
      return this;
    };

    exports.height = function(_) {
      if (!arguments.length) {
        return height;
      }
      height = _;
      h = height - margin.top - margin.bottom;
      sizeChanged = true;
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

    return exports;
  };

  // 使い方  <div id='topologyChart'></div>内にグラフを描画する
  d3iida.topologyChart.example = function() {
    // データをヒアドキュメントから取り出す
    var data = d3iida.heredoc.topology.data;
    console.log(data);

    var topologyChart = d3iida.topologyChart().width(600).height(400);

    // カスタムイベントにハンドラを登録する
    topologyChart.on('customHover', function(d) {
      console.log(d);
    });

    // グラフのコンテナは<div id='topologyChar'>を使う
    var container = d3.select('#topologyChart');

    // コンテナのセレクションにデータを紐付けてcall()する
    container.datum(data).call(topologyChart);

   //
  };
  //
})();
