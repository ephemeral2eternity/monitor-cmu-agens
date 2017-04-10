/**
 * Created by Chen Wang on 4/10/2017.
 */

function scatterISP(json_url) {
    $.getJSON(json_url, function (json) {
        var transitISPPeerData = preprocessISPData(json.transitISP, "peers");
        // console.log(transitISPPeerData);
        scatter(transitISPPeerData, "The # of peers", "QoE anomalies over ISP peers #", "transitISPPeers", false);
        var transitISPSizeData = preprocessISPData(json.transitISP, "size");
        // console.log(transitISPSizeData);
        scatter(transitISPSizeData, "The size of ISP (# of discovered ips in the network)", "QoE anomalies over ISP discovered size", "transitISPSize", false);
        var transitISPGeoData = preprocessISPData(json.transitISP, "geoCoverage");
        // console.log(transitISPGeoData);
        scatter(transitISPGeoData, "The geo-coverage of ISP (# of unique locations)", "QoE anomalies over ISP geographical coverage", "transitISPGeoCoverage", false);
        var transitISPSpanData = preprocessISPData(json.transitISP, "span");
        // console.log(transitISPSpanData);
        scatter(transitISPSpanData, "The maximum span of ISP (The maximum # of hops one session through the ISP)", "QoE anomalies over ISP span", "transitISPSpan", false);
        var accessISPPeerData = preprocessISPData(json.accessISP, "peers");
        // console.log(accessISPPeerData);
        scatter(accessISPPeerData, "The # of peers", "QoE anomalies over ISP peers #", "accessISPPeers", false);
        var accessISPSizeData = preprocessISPData(json.accessISP, "size");
        // console.log(accessISPSizeData);
        scatter(accessISPSizeData, "The size of ISP (# of discovered ips in the network)", "QoE anomalies over ISP discovered size", "accessISPSize", false);
        var accessISPGeoData = preprocessISPData(json.accessISP, "geoCoverage");
        // console.log(accessISPGeoData);
        scatter(accessISPGeoData, "The geo-coverage of ISP (# of unique locations)", "QoE anomalies over ISP geographical coverage", "accessISPGeoCoverage", false);
        var accessISPSpanData = preprocessISPData(json.accessISP, "span");
        // console.log(accessISPSpanData);
        scatter(accessISPSpanData, "The maximum span of ISP (The maximum # of hops one session through the ISP)", "QoE anomalies over ISP span", "accessISPSpan", false);
    });
}

function preprocessISPData(data, xField) {
    // preprocess light
    var outData = {};
    for (var severity in data){
        if (severity == "origin") {
            continue;
        }
        var curList = data[severity];
        // console.log(curList);
        outData[severity] = [];
        for (var i = 0; i < curList.length; i ++) {
            curObj = curList[i];
            // console.log(curObj);
            outData[severity].push({'x':curObj[xField], 'y':curObj["count"], 'label':curObj["isp"], 'as':curObj["as"]});
        }
    }
    return outData;
}

function scatterNetworks(json_url) {
    $.getJSON(json_url, function (json) {
        var transitNetAzureMn = preprocessNetData(json.transitNet, "azMean");
        // console.log(transitISPPeerData);
        scatter(transitNetAzureMn, "The mean latencies to the network from Azure agents", "QoE anomalies over mean latencis from Azure agents", "transitNetAzMn", true);
        var transitNetAzureStd = preprocessNetData(json.transitNet, "azStd");
        // console.log(transitISPSizeData);
        scatter(transitNetAzureStd, "The std of latencies to the network from Azure agents", "QoE anomalies over std of latencis from Azure agents", "transitNetAzStd", true);
        var transitISPGeoData = preprocessNetData(json.transitNet, "plMean");
        // console.log(transitISPGeoData);
        scatter(transitISPGeoData, "The mean latencies to the network from Planetlab agents", "QoE anomalies over std of latencis from Planetlab agents", "transitNetPlMn", true);
        var transitISPSpanData = preprocessNetData(json.transitNet, "plStd");
        // console.log(transitISPSpanData);
        scatter(transitISPGeoData, "The std of latencies to the network from Planetlab agents", "QoE anomalies over std of latencis from Planetlab agents", "transitNetPlStd", true);
        var accessNetAzureMn = preprocessNetData(json.accessNet, "azMean");
        // console.log(accessNetAzureMn);
        scatter(accessNetAzureMn, "The mean latencies to the network from Azure agents", "QoE anomalies over mean latencis from Azure agents", "accessNetAzMn", true);
        var accessNetAzureStd = preprocessNetData(json.accessNet, "azStd");
        // console.log(accessNetAzureStd);
        scatter(accessNetAzureStd, "The std of latencies to the network from Azure agents", "QoE anomalies over std of latencis from Azure agents", "accessNetAzStd", true);
        var accessISPGeoData = preprocessNetData(json.accessNet, "plMean");
        // console.log(accessISPGeoData);
        scatter(accessISPGeoData, "The mean latencies to the network from Planetlab agents", "QoE anomalies over std of latencis from Planetlab agents", "accessNetPlMn", true);
        var accessISPSpanData = preprocessNetData(json.accessNet, "plStd");
        // console.log(accessISPSpanData);
        scatter(accessISPSpanData, "The std of latencies to the network from Planetlab agents", "QoE anomalies over std of latencis from Planetlab agents", "accessNetPlStd", true);
    });
}


function preprocessNetData(data, xField) {
    // preprocess light
    var outData = {};
    for (var severity in data){
        if (severity == "origin") {
            continue;
        }
        var curList = data[severity];
        // console.log(curList);
        outData[severity] = [];
        for (var i = 0; i < curList.length; i ++) {
            curObj = curList[i];
            // console.log(curObj);
            outData[severity].push({'x':curObj[xField], 'y':curObj["count"], 'label':curObj["isp"] + "@" + curObj["city"], 'as':curObj["as"]});
        }
    }
    return outData;
}

function scatter(data, xLabel, title, divTag, allowXDecimal) {
    Highcharts.chart(divTag, {
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: title
        },
        subtitle: {
            text: 'Data on April 4, 2017'
        },
        xAxis: {
            title: {
                enabled: true,
                text: xLabel
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true,
            allowDecimals:allowXDecimal
        },
        yAxis: {
            title: {
                text: '# of QoE anomalies'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 100,
            y: 70,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 5,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: 'Property: {point.x}<br>QoE Anomalies:{point.y}<br>Name: {point.label}<br>AS: {point.as}'
                }
            }
        },
        series: [{
            name: 'Severe',
            color: 'rgba(223, 83, 83, .5)',
            data: data.severe
        }, {
            name: 'Medium',
            color: 'rgba(119, 152, 191, .5)',
            data: data.medium
        }, {
            name: 'Light',
            color: 'rgba(83, 223, 83, .5)',
            data: data.light
        }]
    });
}