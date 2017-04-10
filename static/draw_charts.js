/**
 * Created by Chen Wang on 3/14/2017.
 */
function writeAnomalyIDs(idList){
    var idlist_html_str = ""
    for (var i = 0; i < idList.length; i ++) {
        idlist_html_str += "<a href='/diag/get_anomaly?id=" + idList[i].toString() + "'>" + idList[i].toString() + "</a>";
        idlist_html_str += ", "
    }
    return idlist_html_str
}

function draw_pie_chart(json_url){
    $.getJSON(json_url, function (json) {
        Highcharts.chart('pieChart', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: 0,
                plotShadow: false
            },
            title: {
                text: 'Anomaly<br>Severity',
                align: 'center',
                verticalAlign: 'middle',
                y: 40
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        // distance: -50,
                        format: '<b>{point.name}</b><br>{point.percentage:.1f}%<br>',
                        style: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    },
                    startAngle: -90,
                    endAngle: 90,
                    center: ['50%', '75%']
                }
            },
            series: [{
                type: 'pie',
                name: 'Anomaly Severity',
                innerSize: '50%',
                data: [
                    {name: 'Light', y: json.light.y, label: json.light.label},
                    {name: 'Medium', y: json.medium.y, label: json.medium.label},
                    {name: 'Severe', y: json.severe.y, label: json.severe.label}
                ]
            }]
        });

        var id_list = "";

        id_list += "<ul>";
        id_list += "<li>Light anomaly ids: " + writeAnomalyIDs(json.light.label) + "</li>";
        id_list += "<li>Medium anomaly ids: " + writeAnomalyIDs(json.medium.label) + "</li>";
        id_list += "<li>Severe anomaly ids: " + writeAnomalyIDs(json.severe.label) + "</li>";
        id_list += "</ul>";

        document.getElementById("AnomalyIDlist").innerHTML = id_list;
    });
}

function draw_top_origins(json_url) {
    $.getJSON(json_url, function (json) {
        draw_origin_hist(json.transitISP, "transitISP");
        draw_origin_hist(json.accessISP, "accessISP");
        draw_origin_hist(json.transitNet, "transitNet");
        draw_origin_hist(json.accessNet, "accessNet");
        draw_origin_hist(json.cloudNet, "cloudNet");
        draw_origin_hist(json.server, "server");
    });
}

function draw_origin_hist(data, divTag){
    Highcharts.theme = {
        colors: ['#006400', '#FFA500', '#8B0000', '#4682B4'],
        chart: {
            backgroundColor: null,
            style: {
                fontFamily: 'Signika, serif'
            }
        },
        title: {
            style: {
                color: 'black',
                fontSize: '16px',
                fontWeight: 'bold'
            }
        },
        subtitle: {
            style: {
                color: 'black'
            }
        },
        tooltip: {
            borderWidth: 0
        },
        legend: {
            itemStyle: {
                fontWeight: 'bold',
                fontSize: '18px'
            }
        },
        xAxis: {
            labels: {
                style: {
                    color: '#6e6e70'
                }
            }
        },
        yAxis: {
            labels: {
                style: {
                    color: '#6e6e70'
                }
            }
        },
        plotOptions: {
            series: {
                shadow: true
            },
            candlestick: {
                lineColor: '#404048'
            },
            map: {
                shadow: false
            }
        },

        // Highstock specific
        navigator: {
            xAxis: {
                gridLineColor: '#D0D0D8'
            }
        },
        rangeSelector: {
            buttonTheme: {
                fill: 'white',
                stroke: '#C0C0C8',
                'stroke-width': 1,
                states: {
                    select: {
                        fill: '#D0D0D8'
                    }
                }
            }
        },
        scrollbar: {
            trackBorderColor: '#C0C0C8'
        },

        // General
        background2: '#E0E0E8'

    };

    // Apply the theme
    Highcharts.setOptions(Highcharts.theme);

    var origins;
    if (divTag.includes("ISP")||divTag.includes("Net")) {
        origins = [];
        for (var i = 0; i < data.origin.length; i++) {
            origins.push("AS " + data.origin[i]);
        }
    }
    else {
        origins = data.origin;
    }

    Highcharts.chart(divTag, {
        chart: {
            type: 'column'
        },
        title: {
            text: '# of anomalies at different origins',
            style: {
                fontSize: '20px'
            }
        },
        subtitle: {
            text: '# of anomalies counted by their top 1 origin',
            style: {
                fontSize: '12px'
            }
        },
        xAxis: {
            categories: origins,
            crosshair: true,
            labels: {
                // rotation: -45,
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: '# of anomalies',
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: 'Light',
            data: data.light

        }, {
            name: 'Medium',
            data: data.medium

        }, {
            name: 'Severe',
            data: data.severe

        }, {
            name: 'Total',
            data: data.total
        }]
    });
}