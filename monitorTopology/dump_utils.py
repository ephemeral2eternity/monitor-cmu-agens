from django.db.models import Q
from monitorTopology.models import Anomaly, Cause, ISP, Network, Server, Session, Hop, Edge, Node, Latency

#####################################################################################
## @return: isps_dict ---- the json object that contains info for all isps
#####################################################################################
def dump_all_isps_json():
    isps = ISP.objects.all()

    isps_dict = {}
    for isp in isps:
        isps_dict[isp.ASNumber] = {"name": isp.name, "as": isp.ASNumber, "type":isp.type}
        nets_list = []
        for net in isp.networks.distinct():
            cur_net_dict = {"latitude":float(net.latitude), "longitude":float(net.longitude), "city":net.city, "region":net.region, "country":net.country,
                            "nodes":[], "related_sessions":[], "latencies":{}}
            for node in net.nodes.distinct():
                cur_net_dict["nodes"].append(node.id)
            for session in net.related_sessions.distinct():
                cur_net_dict["related_sessions"].append(session.id)

            azure_probing_lats = net.latencies.filter(agent__agentType="azure")
            planetlab_probing_lats = net.latencies.filter(agent__agentType="planetlab")

            for agent in net.agents.distinct():
                if agent.agentType == "azure":
                    cur_net_dict["latencies"][agent.__str__()] = dump_lat_json(azure_probing_lats)
                else:
                    cur_net_dict["latencies"][agent.__str__()] = dump_lat_json(planetlab_probing_lats)

            nets_list.append(cur_net_dict)
        isps_dict[isp.ASNumber]["networks"] = nets_list
    return isps_dict

#####################################################################################
## @return: nodes_json ---- the json object that contains info for all nodes
#####################################################################################
def dump_all_nodes_json():
    nodes = Node.objects.all()
    nodes_json = {}
    for node in nodes:
        nodes_json[node.id] = {"name": node.name, "ip":node.ip, "type":node.type, "network":node.network.id}
        related_session_ids = []
        for session in node.related_sessions.distinct():
            related_session_ids.append(session.id)

        nodes_json[node.id]["related_sessions"] = related_session_ids

    return nodes_json

#####################################################################################
## @return: sessions_json ---- the json object that contains info for all sessions
#####################################################################################
def dump_all_sessions_json():
    sessions = Session.objects.all()

    sessions_json = {}
    for session in sessions:
        sessions_json[session.id] = {"client":session.client.id, "server":session.server.id}

        hops_dict = {}
        hops = Hop.objects.filter(session=session)
        for hop in hops:
            if hop.hopID not in hops_dict.keys():
                hops_dict[hop.hopID] = []
            hops_dict[hop.hopID].append(hop.node.id)
        links = Edge.objects.filter(Q(src__in=session.route.distinct())&Q(dst__in=session.route.distinct()))
        links_dict = {}
        for link in links:
            links_dict[link.id] = {"isIntra": link.isIntra, "src":link.src.id, "dst":link.dst.id}

        sessions_json[session.id]["hops"] = hops_dict
        sessions_json[session.id]["links"] = links_dict

        server = Server.objects.get(node=session.server)
        session_lats = server.latencies.filter(agent__node=session.client)

        lats_dict = dump_lat_json(session_lats)

        sessions_json[session.id]["latencies"] = lats_dict

    return sessions_json

#####################################################################################
## @params: lats ---- the query set of latency objects
## @return: lats_dict ---- the json object of latencies
#####################################################################################
def dump_lat_json(lats):
    lats_dict = {}
    for lat in lats.all():
        lats_dict[lat.timestamp.timestamp()] = float(lat.latency)

    return lats_dict

# if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    # all_anomalies = get_all_qoe_anomalies()
    # print(all_anomalies)