/**
 * @file draw_networks.js
 * @description Functions that are used to visualize network topology.
 * @author Created by Chen Wang on 3/23/2017.
 */


/**
 * @function drawNetwork(network_id)
 * @description Draw the router topology for a specific network given the network id in database
 * @param network_id the id of the network to draw
 */
function drawNetwork(network_id) {
    // Create a data table with nodes.
    var EDGE_LENGTH_SUB = 50;
    var url = '/get_network_json?id=';

    url = url + network_id.toString();
    console.log(url);
    $.getJSON(url, function (json) {
        var org_nodes = json['nodes'];
        var nodes = [];

        // Create a data table with links.
        var links = json['edges'];
        var edges = [];

        var nodeNumber = org_nodes.length;
        for (var i = 0; i < nodeNumber; i++) {
            nodes.push({
                id: i,
                nid: org_nodes[i]['id'],
                label: org_nodes[i]['name'],
                type: org_nodes[i]['type'],
                image: "/static/" + org_nodes[i]['type'].concat("-router.png"),
                shape: 'image'
            });
        }

        var edgeNumber = links.length;
        for (var j = 0; j < edgeNumber; j++) {
            edges.push({from: links[j]['source'], to: links[j]['target'], length: EDGE_LENGTH_SUB})
        }

        // create a network
        var container = document.getElementById('network');
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
            var url = "/";
            console.log(url);
            document.location.href=url + "get_node?id=" + node["nid"];
        });
    });
}

/**
 * @function drawRouterGraph(ids)
 * @description Draw the router topology for a list of video streaming sessions denoted by ids
 * @param ids the ids of video sessions to be drawn
 */
function drawRouterGraph(ids) {
    var network = null;
    var EDGE_LENGTH_SUB = 50;

    var url = "/get_router_graph_json?";
    var idsNum = ids.length;
    for (var i=0; i<idsNum - 1; i++) {
        url = url + "id=" + ids[i] + "&";
    }
    url = url + "id=" + ids[idsNum - 1];
    console.log(url);

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
                // label: org_nodes[i]['name'],
                type: org_nodes[i]['type'],
                cid: org_nodes[i]['id'],
                // label: "QoE Score: " + org_nodes[i]["qs"] + "\nName: " + org_nodes[i]['name'],
                label: org_nodes[i]['name'],
                image: "/static/" + org_nodes[i]['type'] + ".png",
                shape: 'image'
            });
        }

        var edgeNumber = links.length;
        for (var j = 0; j < edgeNumber; j++) {
            edges.push({from: links[j]['source'], to: links[j]['target'], length: EDGE_LENGTH_SUB})
        }

        // create a network
        var container = document.getElementById('mynetwork');
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
            var url = "/";
            console.log(url);
            document.location.href=url + "get_node?id=" + node['cid'];
        });
    });
}

function drawNetworkGraph(ids) {
    var network = null;
    var EDGE_LENGTH_SUB = 50;

    var url = "/get_net_graph_json?";
    var idsNum = ids.length;
    for (var i=0; i<idsNum - 1; i++) {
        url = url + "id=" + ids[i] + "&";
    }
    url = url + "id=" + ids[idsNum - 1];
    console.log(url);

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
                // label: org_nodes[i]['name'],
                type: org_nodes[i]['type'],
                cid: org_nodes[i]['id'],
                // label: "QoE Score: " + org_nodes[i]["qs"] + "\nName: " + org_nodes[i]['name'],
                label: org_nodes[i]['name'],
                image: "/static/" + org_nodes[i]['type'] + ".png",
                shape: 'image'
            });
        }

        var edgeNumber = links.length;
        for (var j = 0; j < edgeNumber; j++) {
            edges.push({from: links[j]['source'], to: links[j]['target'], length: EDGE_LENGTH_SUB})
        }

        // create a network
        var container = document.getElementById('mynetwork');
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
            var url = "/";
            console.log(url);
            document.location.href=url + "get_" + node['type'] + "?id=" + node['cid'];
        });
    });
}