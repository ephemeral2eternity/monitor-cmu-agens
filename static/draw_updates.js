 /**
 * Created by Chen Wang on 3/11/2017.
 */
function include(arr,obj) {
    return (arr.indexOf(obj) != -1);
}

function drawLatencies(ids_str, obj_typ, agent_typ, divTag) {
    var ids = JSON.parse(("[" + ids_str+ "]"));
    var container = document.getElementById(divTag);
    var url = "/get_latency_json?type=" + obj_typ + "&agent=" + agent_typ;
    for (var i=0; i<ids.length; i ++) {
        url = url + "&id=" + ids[i];
    }

    console.log(url);

    $.getJSON(url, function (json) {
        var items = json.data;
        var data_type = json.objTyp;
        var unique_groups = [];
        var i;
        for (i = 0; i < items.length; i ++) {
            if (include(unique_groups, items[i].group)){
                continue;
            }
            unique_groups.push(items[i].group);
            items[i].label = items[i].y;
        }

        var groups = new vis.DataSet();
        for (var j = 0; j < unique_groups.length; j ++){
            groups.add({
               id: j,
               content: unique_groups[j]
            });
        }

        console.log(groups);

        var dataset = new vis.DataSet(items);
        var options = {
            start: json.start,
            end: json.end,
            legend: true,
            defaultGroup: "",
            dataAxis: {left: {title: {text: "Latency (ms)"}}},
            width: '100%',
            height: '300px',
            style: 'line'
        };
        var Graph2d = new vis.Graph2d(container, dataset, groups, options);
    });
}

function drawUpdates(obj_type, node_ids_str, anomaly_id) {
    var node_ids = JSON.parse(("[" + node_ids_str+ "]"));
    var container = document.getElementById('timecurve');
    var url = "/diag/get_updates_json?type=" + obj_type;
    for (var i=0; i<node_ids.length; i ++) {
        url = url + "&id=" + node_ids[i];
    }

    if (anomaly_id !== undefined) {
        url = url + "&anomaly=" + anomaly_id.toString();
    }

    console.log(url);

    $.getJSON(url, function (json) {
        var items = json.updates;
        var unique_groups = [];
        for (var i = 0; i < items.length; i ++) {
            if (include(unique_groups, items[i].group)) {
                continue;
            }
            unique_groups.push(items[i].group);
            items[i].label = "value: " + items[i].y;
        }

        var groups = new vis.DataSet();
        for (var j = 0; j < unique_groups.length; j ++){
            groups.add({
               id: unique_groups[j],
               content: "Session " + unique_groups[j].toString()
            });
        }

        console.log(unique_groups);
        console.log(json);

        var dataset = new vis.DataSet(items);
        var options = {
            start: json.start,
            end: json.end,
            legend: true,
            dataAxis: {left: {title: {text: "QoE updates"}}},
            width: '100%',
            height: '300px',
            style: 'line'
        };
        var Graph2d = new vis.Graph2d(container, dataset, groups, options);
    });
}

function drawStatus(obj_type, obj_ids_str, anomaly_id) {
    var obj_ids = JSON.parse(("[" + obj_ids_str+ "]"));
    var url = "/diag/get_status_json?type=" + obj_type;
    for (var i=0; i<obj_ids.length; i ++) {
        url = url + "&id=" + obj_ids[i];
    }

    if (anomaly_id !== undefined) {
        url = url + "&anomaly=" + anomaly_id.toString();
    }

    console.log(url);

    $.getJSON(url, function (json) {
        var items = json.status;
        var unique_groups = [];
        for (var i = 0; i < items.length; i ++) {
            items[i].className = items[i].content;
            if (include(unique_groups, items[i].group)) {
                continue;
            }
            unique_groups.push(items[i].group);
        }

        var groups = new vis.DataSet();
        for (var j = 0; j < unique_groups.length; j ++){
            groups.add({
               id: unique_groups[j],
               content: "Session " + unique_groups[j].toString()
            });
        }

        console.log(unique_groups);
        console.log(json);

        var dataset = new vis.DataSet(items);
        // create visualization
        var container = document.getElementById('timecurve');
        var options = {
            groupOrder: 'content'  // groupOrder can be a property name or a sorting function
        };

        var timeline = new vis.Timeline(container);
        timeline.setOptions(options);
        timeline.setGroups(groups);
        timeline.setItems(items);

    });
}

