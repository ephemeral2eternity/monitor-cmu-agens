from monitorTopology.models import Session, Node, Server, Agent, ISP, Network, Edge, NetEdge, PeeringEdge, Latency, Hop, Subnetwork, ServerProbing, NetProbing
from monitorTopology.ipinfo import *
from django.utils import timezone
from django.db import transaction
from monitorTopology.azure_agents import *
from monitorTopology.comm_utils import *
from monitorTopology.lat_utils import *
import math
import sys
import requests
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__package__)

### @function add_node(node_ip, nodeTyp="router")
#   @params:
#       node_ip : the ip address of a given node
#       nodeTyp : the type of a given node. Can be client, server, router in a video session
#                 or pl_agent, which is a probing agent in PlanetLab
#                 or azure_agent, which is a probing agent in Azure
#   @return: the node object in Node model
@transaction.atomic
def add_node(node_ip, nodeTyp="router", nodeName=None, netTyp="transit"):
    try:
        node = Node.objects.get(ip=node_ip)
    except:
        node_info = get_node_info(node_ip)

        try:
            node_isp = ISP.objects.get(ASNumber=node_info["AS"])
        except:
            node_isp = ISP(ASNumber=node_info["AS"], name=node_info["ISP"])
        node_isp.type = netTyp
        node_isp.save()

        latitude = float(node_info['latitude'])
        latitude_str = '{0:.6f}'.format(latitude)
        longitude = float(node_info['longitude'])
        longitude_str = '{0:.6f}'.format(longitude)
        # print("AS " + str(node_isp.ASNumber) + "(" + latitude_str + "," + longitude_str + ")" )
        try:
            node_network = Network.objects.get(isp=node_isp, latitude=latitude_str, longitude=longitude_str)
        except:
            node_network = Network(isp=node_isp, latitude=latitude_str, longitude=longitude_str, city=node_info["city"], region=node_info["region"], country=node_info["country"])
            node_network.save()


        if nodeName:
            node = Node(ip=node_ip, name=nodeName, type=nodeTyp, network=node_network)
        else:
            node = Node(ip=node_ip, name=node_info['name'], type=nodeTyp, network=node_network)
        node.save()

        if node not in node_network.nodes.all():
            node_network.nodes.add(node)
            node_network.save()

        if node_network not in node_isp.networks.all():
            node_isp.networks.add(node_network)
            node_isp.save()

    ## Wrap up the server node
    if nodeTyp == "server":
        try:
            srv = add_server(node)
        except:
            print("Failed to wrap up the server node as server object: " + node.ip)

    return node

### @function init_azure_nodes()
#   @descr: Add all Azure nodes
#   @params:
#       node: the ip of the agent to be added
def init_azure_nodes():
    azure_nodes = list_azure_agents("monitoring", "agent-")
    for azure_node in azure_nodes:
        az_node = add_node(azure_node["ip"], nodeTyp="client", nodeName=azure_node["name"], netTyp="cloud")

### @function add_server(node)
#   @descr: Wrap up a server node as a server object
#   @params:
#       node: the ip of the agent to be added
def add_server(node):
    try:
        srv = Server.objects.get(node=node)
    except:
        srv = Server(node=node)
        srv.save()
    return srv

### @function add_agent(agent_ip, agent_type)
#   @descr: Add an agent by its ip
#   @params:
#       agent_ip: the ip of the agent to be added
def add_agent(agent_ip):
    agent_node = add_node(agent_ip, nodeTyp="client", netTyp="access")
    if agent_node.network.isp.name.__contains__("Microsoft"):
        agent_typ = "azure"
    ## Check if the ISP is AWS or Google here.
    # elif agent_node.network.isp.name.__contains__("Microsoft"):
    else:
        agent_typ = "planetlab"
    try:
        agent = Agent.objects.get(node=agent_node, agentType=agent_typ)
    except:
        agent = Agent(node=agent_node, agentType=agent_typ)
        agent.save()
    return agent


### @function add_private_node(pre_node, dst_isp)
#   @descr: Add an "*" node in the network
#   @params:
#       pre_node : previous known node
def add_private_node(pre_node, nodeTyp="router"):
    cur_net = pre_node.network
    try:
        private_node = Node.objects.get(ip="*", network=pre_node.network)
    except:
        private_node = Node(ip="*", name="*", type=nodeTyp, network=cur_net)
        private_node.save()
        if private_node not in cur_net.nodes.all():
            cur_net.nodes.add(private_node)

        # update the link between "*" node and the closest given node.
        update_edge(pre_node, private_node, 500)

    #if private_node not in pre_node.network.nodes.all():
    #    pre_node.network.nodes.add(private_node)

    return private_node

### @function update_peering(src_isp, dst_isp)
#   @descr: Save the peering relationship in the database
#   @params:
#       src_isp : the source ISP in the peering link
#       dst_isp : the destination ISP in the peering link
@transaction.atomic
def update_peering(src_isp, dst_isp):
    if src_isp.ASNumber == dst_isp.ASNumber:
        return

    if src_isp.ASNumber > dst_isp.ASNumber:
        tmp_isp = src_isp
        src_isp = dst_isp
        dst_isp = tmp_isp

    try:
        peering_link = PeeringEdge.objects.get(srcISP=src_isp, dstISP=dst_isp)
    except:
        peering_link = PeeringEdge(srcISP=src_isp, dstISP=dst_isp)
        peering_link.save()


### @function update_net_edge(srcNet, dstNet, isIntra)
#   @descr: Save the edge between two networks in the database
#   @params:
#       srcNet : the source network of the link
#       dstNet : the destination network of the link
#       isIntra : denotes if the link is an intra ISP link
@transaction.atomic
def update_net_edge(srcNet, dstNet, isIntra):
    if srcNet.id == dstNet.id:
        return

    if srcNet.id > dstNet.id:
        tmpNet = srcNet
        srcNet = dstNet
        dstNet = tmpNet

    try:
        net_edge = NetEdge.objects.get(srcNet=srcNet, dstNet=dstNet)
    except:
        net_edge = NetEdge(srcNet=srcNet, dstNet=dstNet, isIntra=isIntra)
        net_edge.save()


### @function update_edge(src_node, dst_node, latency)
#   @params:
#       route : a json object of a traceroute session info
#               The key denotes the hop number. 0 denotes the client and the maximum key denotes the server
#               Each value object contains info {"ip": hop_ip_x.x.x.x, "name": hop_hostname, "time": time_to_get_to_the_hop}
def update_edge(src_node, dst_node, latency):
    if src_node.ip == dst_node.ip:
        return

    if src_node.ip > dst_node.ip:
        tmp_node = src_node
        src_node = dst_node
        dst_node = tmp_node

    try:
        link = Edge.objects.get(src=src_node, dst=dst_node)
    except:
        link_is_intra = (src_node.network.isp.ASNumber == dst_node.network.isp.ASNumber)
        link = Edge(src=src_node, dst=dst_node, isIntra=link_is_intra)
        link.save()

        # Add peering link if necessary
        if not link_is_intra:
            update_peering(src_node.network.isp, dst_node.network.isp)

        # Add network_edge if neccessary
        if src_node.network.id != dst_node.network.id:
            update_net_edge(src_node.network, dst_node.network, link_is_intra)

    link_latency = Latency(latency=latency, timestamp=timezone.now())
    link_latency.save()

    link.latencies.add(link_latency)
    link.save()

### add_hop(hop, hop_id, session)
#   @description: add the current node object as a hop in the session
#   @params:
#       hop : the node object of current hop
#       hop_id : The hop id of current id in the session
#       session : The session the hop is on.
def add_hop(hop, hop_id, session):
    ## Add hop of current node
    try:
        cur_hop = Hop.objects.get(node=hop, hopID=hop_id, session=session)
    except:
        cur_hop = Hop(node=hop, hopID=hop_id, session=session)
        cur_hop.save()

### add_hop(hop, hop_id, session)
#   @description: add the current network object as a subnet in the session
#   @params:
#       node_net : the network object
#       net_id : the sequence number of the network in the session
#       session : The session the network is on.
def add_subnet(node_net, net_id, session):
    try:
        cur_net = Subnetwork.objects.get(network=node_net, netID=net_id, session=session)
    except:
        cur_net = Subnetwork(network=node_net, netID=net_id, session=session)
        cur_net.save()

### @function add_route(route)
#   @params:
#       route : a json object of a traceroute session info
#               The key denotes the hop number. 0 denotes the client and the maximum key denotes the server
#               Each value object contains info {"ip": hop_ip_x.x.x.x, "name": hop_hostname, "time": time_to_get_to_the_hop}
def add_route(route):
    hop_ids = sorted(route.keys(), key=int)
    client = route[hop_ids[0]]
    server = route[hop_ids[-1]]
    if (client['ip'] == "*") or (server["ip"] == "*"):
        return

    client_node = add_node(client["ip"], "client", client["name"], "access")
    server_node = add_node(server["ip"], "server", server["name"], "cloud")

    session = add_session(client_node, server_node)
    sub_net_id = 0
    add_hop(client_node, int(hop_ids[0]), session)
    add_subnet(client_node.network, sub_net_id, session)

    pre_node = client_node
    pre_time = client["time"]
    for hop_id in hop_ids[1:-1]:
        cur_hop = route[hop_id]
        if (cur_hop["ip"] == "*") or (is_reserved(cur_hop["ip"])):
            cur_node = add_private_node(pre_node)
            add_hop(cur_node, hop_id, session)
            pre_node = cur_node
            continue

        cur_node = add_node(cur_hop["ip"])
        cur_time = cur_hop["time"]

        latency = cur_time - pre_time
        if latency < 0:
            latency = 0
        update_edge(pre_node, cur_node, latency)
        add_hop(cur_node, hop_id, session)
        if cur_node.network.id != pre_node.network.id:
            sub_net_id += 1
            add_subnet(cur_node.network, sub_net_id, session)

        pre_node = cur_node
        pre_time = cur_time

    latency = server["time"] - pre_time
    if latency < 0:
        latency = 0
    update_edge(pre_node, server_node, latency)
    add_hop(server_node, int(hop_ids[-1]), session)

    if server_node.network.id != pre_node.network.id:
        sub_net_id += 1
        add_subnet(server_node.network, sub_net_id, session)

### @function add_session(client, server)
#   @params:
#       client : the client node object of the session
#       server : the server node object of the session
def add_session(client, server):
    try:
        session = Session.objects.get(client=client, server=server)
    except:
        session = Session(client=client, server=server)
        session.save()
    return session


### @function get_agent(obj, agentType)
#   @params:
#       obj : the server/network to probe
#       agentType : the type of agent to obtain
#
def get_agent(obj, agentType):
    agents = Agent.objects.filter(agentType=agentType).all()

    obj_type = obj.get_class_name()
    if obj_type == "server":
        obj_lat = obj.node.network.latitude
        obj_lon = obj.node.network.longitude
    # By default, the else denotes the "network" case
    else:
        obj_lat = obj.latitude
        obj_lon = obj.longitude

    if agents.count() > 0:
        obj_agent = agents[0]
        min_dist = get_distance(obj_lat, obj_lon, obj_agent.node.network.latitude, obj_agent.node.network.longitude)
        for agent in agents[1:]:
            cur_dist = get_distance(obj_lat, obj_lon, agent.node.network.latitude, agent.node.network.longitude)
            if cur_dist < min_dist:
                obj_agent = agent
                min_dist = cur_dist
            elif cur_dist == min_dist:
                if obj_type == "server":
                    obj_agent_cnt = obj_agent.servers.count()
                    cur_agent_cnt = agent.servers.count()
                else:
                    obj_agent_cnt = obj_agent.networks.count()
                    cur_agent_cnt = agent.networks.count()
                if obj_agent_cnt > cur_agent_cnt:
                    obj_agent = agent
                    min_dist = cur_dist

        return obj_agent
    else:
        return None

## @function get_distance(lat1, lon1, lat2, lon2)
#   @params:
#       lat1, lon1 : the latitude and longitude of the first object
#       lat2, lon2 : the latitude and longitude of the first object
#   @return: dist ---- the geographical distance
def get_distance(lat1, lon1, lat2, lon2):
    dist = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    return dist

## @function probe_networks()
#  @description: get probing agents for all networks.
def probe_networks():
    NetProbing.objects.all().delete()
    nets = Network.objects.all()
    agent_typs = ["planetlab", "azure"]

    for net in nets:
        for agentTyp in agent_typs:
            cur_agent = get_agent(net, agentTyp)
            if cur_agent:
                netProbe = NetProbing(network=net, agent=cur_agent)
                netProbe.save()

## @function probe_servers()
#  @description: get probing agents for all servers.
def probe_servers():
    ServerProbing.objects.all().delete()

    servers = Server.objects.all()
    agent_typs = ["planetlab", "azure"]

    for srv in servers:
        for agentTyp in agent_typs:
            cur_agent = get_agent(srv, agentTyp)
            if cur_agent:
                srvProbe = ServerProbing(server=srv, agent=cur_agent)
                srvProbe.save()

# @descr: Get the anomaly counts per origin type for histogram graphs
def getQoEAnomaliesStats():
    curfilePath = os.path.abspath(__file__)
    curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))  # this will return current directory in which python file resides.
    parentDir = os.path.abspath(os.path.join(curDir, os.pardir))  # this will return parent directory.
    outputJsonName = "anomaly_stats_" + time.strftime("%m%d") + ".json"

    if os.path.exists(parentDir + "/databackup/" + outputJsonName):
        with open(parentDir + "/databackup/" + outputJsonName) as json_data:
            all_origin_stats_dict = json.load(json_data)
            return all_origin_stats_dict

    all_qoe_anomalies = get_all_qoe_anomalies()
    all_origin_stats_dict = {}
    for origin_type in all_qoe_anomalies.keys():
        cur_anomalies = all_qoe_anomalies[origin_type]
        top_origins = sorted(cur_anomalies.keys())
        origin_stats_dict = {
            "origin": top_origins,
            "light": [],
            "medium": [],
            "severe": [],
            "total": []
        }

        for origin in top_origins:
            anomaly_pts = cur_anomalies[origin]
            cur_obj = {
                "light": {"y": 0, "label": ""},
                "medium": {"y": 0, "label": ""},
                "severe": {"y": 0, "label": ""},
                "total": {"y": 0, "label": ""}
            }

            for anomaly_pt in anomaly_pts:
                cur_obj[anomaly_pt["type"]]["y"] += anomaly_pt["count"]
                cur_obj["total"]["y"] += anomaly_pt["count"]
                cur_obj[anomaly_pt["type"]]["label"] += str(anomaly_pt["id"]) + ","
                cur_obj["total"]["label"] += str(anomaly_pt["id"]) + ","

            origin_stats_dict["light"].append(cur_obj["light"])
            origin_stats_dict["medium"].append(cur_obj["medium"])
            origin_stats_dict["severe"].append(cur_obj["severe"])
            origin_stats_dict["total"].append(cur_obj["total"])

        # print(origin_stats_dict)
        all_origin_stats_dict[origin_type] = origin_stats_dict
        with open(parentDir + "/databackup/" + outputJsonName, "w") as outFile:
            json.dump(all_origin_stats_dict, outFile, sort_keys=True, indent=4, ensure_ascii=True)
    return all_origin_stats_dict


def get_scatter_origin_anomalies_json():
    logger.info("Running get_scatter_origin_anomalies_json")
    all_origin_stats_dict = getQoEAnomaliesStats()
    curfilePath = os.path.abspath(__file__)
    curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))  # this will return current directory in which python file resides.
    parentDir = os.path.abspath(os.path.join(curDir, os.pardir))  # this will return parent directory.
    outputJsonName = "scatter_" + time.strftime("%m%d") + ".json"

    if os.path.exists(parentDir + "/databackup/" + outputJsonName):
        with open(parentDir + "/databackup/" + outputJsonName) as json_data:
            scatter_origin_json = json.load(json_data)
            return scatter_origin_json

    scatter_origin_json = {}
    for origin_type in all_origin_stats_dict.keys():
        if origin_type not in scatter_origin_json.keys():
            scatter_origin_json[origin_type] = {}
        for severity in all_origin_stats_dict[origin_type].keys():
            ## Ignore the origin field
            if severity == "origin":
                continue

            if severity not in scatter_origin_json[origin_type].keys():
                scatter_origin_json[origin_type][severity] = []
            cur_anomaly_cnts = all_origin_stats_dict[origin_type][severity]
            origins = all_origin_stats_dict[origin_type]["origin"]
            if "ISP" in origin_type:
                for i, origin in enumerate(origins):
                    # print("Processing ISP with AS number : " + origin)
                    try:
                        isp = ISP.objects.get(ASNumber=origin)
                        # print("Obtained ISP with AS number : " + origin)
                        anomalyCnt = cur_anomaly_cnts[i]["y"]
                        if anomalyCnt > 0:
                        # print(anomalyCnt)
                            scatter_origin_json[origin_type][severity].append({"as":isp.ASNumber, "isp":isp.name, "geoCoverage":isp.get_geo_coverage(),
                                        "peers": len(isp.get_peers()), "size":isp.get_node_size(), "span":isp.get_max_span(), "count":anomalyCnt})
                    except:
                        logger.info("Unexpected error:" + str(sys.exc_info()[0]))
                        logger.info("ISP AS " + origin + " was not monitored. The origin is with label: " +
                              cur_anomaly_cnts[i]["label"])
                        continue
            elif "Net" in origin_type:
                for i, origin in enumerate(origins):
                    netAS, lat, lon = origin.split(",")
                    # print("Processing network with AS: " + netAS + " and location at (" + lat + "," + lon + ")")
                    try:
                        isp = ISP.objects.get(ASNumber=netAS)
                        # print("Get ISP object with AS: " + netAS)
                        net = Network.objects.get(isp=isp, latitude=lat, longitude=lon)
                        # print("Obtained network object with AS: " + netAS + " at (" + lat + "," + lon + ")")
                        azLatMn, azLatStd = get_lat_stat(net.latencies.filter(agent__agentType="azure"))
                        plLatMn, plLatStd = get_lat_stat(net.latencies.filter(agent__agentType="planetlab"))

                        anomalyCnt = cur_anomaly_cnts[i]["y"]
                        # print(anomalyCnt)
                        if anomalyCnt > 0:
                            scatter_origin_json[origin_type][severity].append(
                                {"as": net.isp.ASNumber, "isp": net.isp.name, "name": net.__str__(), "city":net.city, "region":net.region,
                                 "country":net.country, "size": net.get_nodes_num(), "span":net.get_max_size(),
                                 "azMean":azLatMn, "azStd":azLatStd, "plMean":plLatMn, "plStd":plLatStd, "count":anomalyCnt})
                    except:
                        logger.info("Unexpected error:" + str(sys.exc_info()[0]))
                        logger.info("Network " + origin + " was not monitored. The origin is with label: " +
                              cur_anomaly_cnts[i]["label"])
                        continue
            elif origin_type == "server":
                for i, origin in enumerate(origins):
                    # print("Processing server with ip : " + origin)
                    try:
                        server = Server.objects.get(node__ip=origin)
                        # print("Obtained server with ip : " + origin)
                        azLatMn, azLatStd = get_lat_stat(server.latencies.filter(agent__agentType="azure"))
                        plLatMn, plLatStd = get_lat_stat(server.latencies.filter(agent__agentType="planetlab"))

                        anomalyCnt = cur_anomaly_cnts[i]["y"]
                        #print(anomalyCnt)
                        if anomalyCnt > 0:
                            scatter_origin_json[origin_type][severity].append(
                                {"ip": server.node.ip, "city": server.node.network.city, "region":server.node.network.region, "country":server.node.network.country,
                                  "azMean":azLatMn, "azStd":azLatStd, "plMean":plLatMn, "plStd":plLatStd, "count":anomalyCnt})
                    except:
                        logger.info("Unexpected error:" + str(sys.exc_info()[0]))
                        logger.info("Server with IP " + origin + " was not monitored. The origin is with label: " +
                              cur_anomaly_cnts[i]["label"])
                        continue
            else:
                continue

    with open(parentDir + "/databackup/" + outputJsonName, "w") as outFile:
        json.dump(scatter_origin_json, outFile, sort_keys=True, indent=4, ensure_ascii=True)

    return scatter_origin_json
