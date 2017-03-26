# data_utils.py
# @descr: read data from mysql data bases and dump those to json for visualization purpose
# @author: Chen Wang @ CMU, Mar. 24, 2017
from monitorTopology.models import Session, Edge, Node, NetEdge

### @function get_router_graph_json(session_ids)
#   @descr: Get router topology data from database and dump it to a json that is for vis.js topology visualization
#   @params:
#       session_ids : a list of sessions to show the router level topology
#   @return: graph ---- the json data for visualization
def get_router_graph_json(session_ids):
    graph = {"links": [], "nodes": []}
    nodes = []
    for session_id in session_ids:
        session = Session.objects.get(id=session_id)

        for node in session.route.all().distinct():
            if node.id not in nodes:
                nodes.append(node.id)
                graph["nodes"].append(
                {"name": node.name, "type": node.type, "id": node.id, "ip": node.ip})

    edges = Edge.objects.filter(src_id__in=nodes, dst_id__in=nodes)
    for edge in edges.all():
        srcID = nodes.index(edge.src.id)
        dstID = nodes.index(edge.dst.id)
        if edge.isIntra:
            link_group = "intra"
        else:
            link_group = "inter"
        graph["links"].append({"source": srcID, "target": dstID, "group": link_group})

    return graph

### @function get_network_graph_json(session_ids)
#   @descr: Get network topology data from database and dump it to a json that is for vis.js topology visualization
#   @params:
#       session_ids : a list of sessions to show the router level topology
#   @return: graph ---- the json data for visualization
def get_network_graph_json(session_ids):
    net_nodes = []
    graph = {"links": [], "nodes": []}
    for session_id in session_ids:
        session = Session.objects.get(id=session_id)

        for net in session.sub_networks.all().distinct():
            if net.id not in net_nodes:
                net_nodes.append(net.id)
                graph["nodes"].append({"name": net.isp.name, "type": "network", "id": net.id})

    edges = NetEdge.objects.filter(srcNet_id__in=net_nodes, dstNet_id__in=net_nodes).all().distinct()
    for edge in edges.all():
        srcID = net_nodes.index(edge.srcNet.id)
        dstID = net_nodes.index(edge.dstNet.id)
        if edge.isIntra:
            link_group = "intra"
        else:
            link_group = "inter"
        graph["links"].append({"source": srcID, "target": dstID, "group": link_group})

    return  graph