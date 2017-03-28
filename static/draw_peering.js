/**
 * Created by chenw on 3/26/17.
 */

function drawPeering(ids) {
    var url = "/get_isp_peers_json?";
    var idsNum = ids.length;
    for (var i=0; i<idsNum - 1; i++) {
        url = url + "as=" + ids[i] + "&";
    }
    url = url + "as=" + ids[idsNum - 1];
    console.log(url);
}