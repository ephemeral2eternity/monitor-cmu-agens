/**
 * Created by chenw on 3/26/17.
 */
function drawISPMap(ids) {
    var url = "/get_isp_nets_json?";
    var idsNum = ids.length;
    for (var i=0; i<idsNum - 1; i++) {
        url = url + "as=" + ids[i] + "&";
    }
    url = url + "as=" + ids[idsNum - 1];
    console.log(url);

    var H = Highcharts,
    map = H.maps['custom/world'],
    chart;


    // Add series with state capital bubbles
    $.getJSON(url, function (json) {
        var data = [];

        var seriesData = [{
            name: 'Basemap',
            mapData: map,
            borderColor: 'rgba(200, 200, 200, 0.2)',
            nullColor: 'rgba(200, 200, 200, 0.2)',
            showInLegend: false
        }];

        var cor_id = 0;

        for (var ispName in json){
            var cur_data = [];
            $.each(json[ispName], function () {
                this.z = this.netsize;
                cur_data.push(this);
            });
            seriesData.push({
                type: 'mapbubble',
                dataLabels: {
                    enabled: true,
                    format: '{point.asn}'
                },
                name: ispName,
                data: cur_data,
                minSize: 5,
                maxSize: 50,
                enableMouseTracking: true,
                color: H.getOptions().colors[cor_id],
                tooltip: {
                    pointFormat: '{point.asn}<br>' +
                        'Lat: {point.lat}<br>' +
                        'Lon: {point.lon}<br>' +
                        'Net Size: {point.netsize}'
                }
            });
            cor_id += 1;
        }

        chart = Highcharts.mapChart('ispMap', {

            title: {
                text: 'ISP locations'
            },


            xAxis: {
                crosshair: {
                    zIndex: 5,
                    dashStyle: 'dot',
                    snap: false,
                    color: 'gray'
                }
            },

            yAxis: {
                crosshair: {
                    zIndex: 5,
                    dashStyle: 'dot',
                    snap: false,
                    color: 'gray'
                }
            },

            legend: {
                enabled: true
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    verticalAlign: 'bottom'
                }
            },

            series: seriesData
        });
    });
}

function drawMap() {
    var url = "/get_map_json";
    console.log(url);

    var H = Highcharts,
    map = H.maps['custom/world'],
    chart;


    // Add series with state capital bubbles
    $.getJSON(url, function (json) {
        var server_data = json.server;
        var agent_data = json.agent;
        var network_data = json.network;
        var cur_net_data = [];

        $.each(network_data, function () {
            this.z = this.netsize;
            cur_net_data.push(this);
        });

        var seriesData = [{
            name: 'Basemap',
            mapData: map,
            borderColor: 'rgba(200, 200, 200, 0.2)',
            nullColor: 'rgba(200, 200, 200, 0.2)',
            showInLegend: false
        }];

        seriesData.push({
            type: 'mapbubble',
            dataLabels: {
                enabled: true,
                format: '{point.asn}'
            },
            name: "Network",
            data: cur_net_data,
            minSize: 5,
            maxSize: 50,
            enableMouseTracking: true,
            color: H.getOptions().colors[0],
            tooltip: {
                pointFormat: '{point.asn}<br>' +
                    'ID: {point.netID}<br>' +
                    'Lat: {point.lat}<br>' +
                    'Lon: {point.lon}<br>' +
                    'Net Size: {point.netsize}'
            }
        });

        seriesData.push({
            type: 'mappoint',
            dataLabels: {
                enabled: true,
                format: '{point.name}'
            },
            name: "Server",
            data: server_data,
            enableMouseTracking: true,
            color: H.getOptions().colors[1],
            tooltip: {
                pointFormat: '{point.ip}<br>' +
                    'Name: {point.name}<br>' +
                    'Lat: {point.lat}<br>' +
                    'Lon: {point.lon}<br>'
            }
        });

        seriesData.push({
            type: 'mappoint',
            dataLabels: {
                enabled: true,
                format: '{point.name}'
            },
            name: "Agent",
            data: agent_data,
            enableMouseTracking: true,
            color: H.getOptions().colors[2],
            tooltip: {
                pointFormat: '{point.ip}<br>' +
                    'Name: {point.name}<br>' +
                    'Lat: {point.lat}<br>' +
                    'Lon: {point.lon}<br>'
            }
        });

        chart = Highcharts.mapChart('allMap', {

            title: {
                text: 'Server, networks, and agents\' locations'
            },


            xAxis: {
                crosshair: {
                    zIndex: 5,
                    dashStyle: 'dot',
                    snap: false,
                    color: 'gray'
                }
            },

            yAxis: {
                crosshair: {
                    zIndex: 5,
                    dashStyle: 'dot',
                    snap: false,
                    color: 'gray'
                }
            },

            legend: {
                enabled: true
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    verticalAlign: 'bottom'
                }
            },

            series: seriesData
        });
    });
}
