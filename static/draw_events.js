/**
 * Created by Chen Wang on 3/14/2017.
 */
/**
 * Zoom the timeline a given percentage in or out
 * @param {Number} percentage   For example 0.1 (zoom out) or -0.1 (zoom in)
 */
function zoom (percentage) {
    var range = timeline.getWindow();
    var interval = range.end - range.start;

    timeline.setWindow({
        start: range.start.valueOf() - interval * percentage,
        end:   range.end.valueOf()   + interval * percentage
    });
}

/**
 * Move the timeline a given percentage to left or right
 * @param {Number} percentage   For example 0.1 (left) or -0.1 (right)
 */
function move (percentage) {
    var range = timeline.getWindow();
    var interval = range.end - range.start;

    timeline.setWindow({
        start: range.start.valueOf() - interval * percentage,
        end:   range.end.valueOf()   - interval * percentage
    });
}

function include(arr,obj) {
    return (arr.indexOf(obj) != -1);
}

function draw_anomalies(anomaly_url) {
    $.getJSON(anomaly_url, function (json) {
        var items = json.anomalies;
        var unique_groups = [];
        for (var i = 0; i < items.length; i ++) {
            items[i].type = "point";
            items[i].className = items[i].anomaly_type;
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
        // create a dataset with items
        // note that months are zero-based in the JavaScript Date object, so month 3 is April
        var vis_items = new vis.DataSet(items);

        // create visualization
        var container = document.getElementById('anomalies');
        var options = {
            // option groupOrder can be a property name or a sort function
            // the sort function must compare two groups and return a value
            //     > 0 when a > b
            //     < 0 when a < b
            //       0 when a == b
            groupOrder: function (a, b) {
                return a.value - b.value;
            },
            editable: false,
            orientation: 'top',
            showCurrentTime: false,
            stack:false
        };

        var timeline = new vis.Timeline(container);
        timeline.setOptions(options);
        timeline.setGroups(groups);
        timeline.setItems(vis_items);

        // attach events to the navigation buttons
        document.getElementById('zoomIn').onclick = function () {
            zoom(-0.2);
        };
        document.getElementById('zoomOut').onclick = function () {
            zoom(0.2);
        };
        document.getElementById('moveLeft').onclick = function () {
            move(0.2);
        };
        document.getElementById('moveRight').onclick = function () {
            move(-0.2);
        };
        document.getElementById('fit').onclick = function () {
            timeline.fit();
        };

    });
}