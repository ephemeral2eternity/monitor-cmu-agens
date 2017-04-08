/**
 * Created by chenw on 4/7/17.
 */

function drawNetLat(netType, agentType, divTag) {
    // Create a data table with nodes.
    var url = '/stat_net_lat?net=' + netType + "&agent=" + agentType;
    console.log(url);
    $.getJSON(url, function (json) {
        var data = json.data;
        var latData = [];
        for (var i = 0; i < data.length; i ++) {
            latData.push([data[i].name, data[i].mean])
        }
        console.log(latData);

        Highcharts.chart(divTag, {
            chart: {
                type: 'column'
            },
            title: {
                text: 'The mean latencies over networks'
            },
            subtitle: {
                text: 'Source: <a href="/show_networks">Show Network Details</a>'
            },
            xAxis: {
                type: 'category',
                labels: {
                    rotation: -45,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
                min: -1,
                title: {
                    text: 'Mean Latency (ms)'
                }
            },
            legend: {
                enabled: false
            },
            tooltip: {
                pointFormat: 'Mean Latency: <b>{point.y:.1f} ms</b>'
            },
            series: [{
                name: 'Latency',
                data: latData,
                dataLabels: {
                    enabled: true,
                    rotation: -90,
                    color: '#FFFFFF',
                    align: 'right',
                    format: '{point.y:.1f}', // one decimal
                    y: 10, // 10 pixels down from the top
                    style: {
                        fontSize: '13px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            }]
        });
    });
}
