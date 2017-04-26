/**
 * Created by Chen Wang on 4/26/2017.
 */
function drawLocalization(locator, anomaly_id, divTag) {
    var nodes = null;
    var edges = null;
    var network = null;

    var EDGE_LENGTH_MAIN = 50;
    var EDGE_LENGTH_SUB = 10;

    // Called when the Visualization API is loaded.
    var url = 'http://'+ locator + '.cmu-agens.com/diag/get_ano_graph_json?id=' + anomaly_id.toString();
    $.getJSON(url, function (json) {
        var org_nodes = json['nodes'];
        var nodes = [];

        // Create a data table with links.
        var links = json['links'];
        var edges = [];

        var nodeNumber = org_nodes.length;
        for (var i = 0; i < nodeNumber; i++) {
            nodes.push({
                id: i,
                nodeid: org_nodes[i]['id'],
                label: org_nodes[i]['name'],
                type: org_nodes[i]['type'],
                image: "/static/" + org_nodes[i]['group'] + "-" + org_nodes[i]['type'] + ".png",
                shape: 'image'
            });
        }

        var edgeNumber = links.length;
        for (var j = 0; j < edgeNumber; j++) {
            edges.push({from: links[j]['source'], to: links[j]['target'], length: EDGE_LENGTH_SUB})
        }

        // create a network
        var container = document.getElementById(divTag);
        var data = {
            nodes: nodes,
            edges: edges
        };
        var options = {
            layout: {
                improvedLayout:true,
                hierarchical: {
                    enabled:false,
                    direction: "RL"
                }
            }
        };
        network = new vis.Network(container, data, options);
        network.on('selectNode', function (params) {
            console.log(params);
            var nodeID = params['nodes'][0];
            console.log(nodeID);
            var node = nodes[nodeID];
            console.log(node);
            var url = "http://"+ locator + ".cmu-agens.com/diag/";
            console.log(url);
            document.location.href=url + "get_node?id=" + node['nodeid'];
        });
    });
}