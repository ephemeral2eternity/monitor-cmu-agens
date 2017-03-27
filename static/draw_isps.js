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
