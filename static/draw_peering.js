/**
 * Created by chenw on 3/26/17.
 */

function drawISPPeering(ids) {
    var url = "/get_isp_peers_json?";
    var idsNum = ids.length;
    for (var i=0; i<idsNum - 1; i++) {
        url = url + "as=" + ids[i] + "&";
    }
    url = url + "as=" + ids[idsNum - 1];
    console.log(url);

    // Add series with state capital bubbles
    $.getJSON(url, function (json) {
        var data = json;
        /*var data = {
            packageNames: ['Main', 'A', 'B'],
                matrix: [[0, 1, 1], // Main depends on A and B
                [0, 0, 1], // A depends on B
                [0, 0, 0]] // B doesn't depend on A or Main
            };*/

        console.log(data);

        var chart = d3.chart.dependencyWheel()
            .width(1400)
            .margin(300);
        d3.select('#ispPeering')
          .datum(data)
          .call(chart);
    });
}