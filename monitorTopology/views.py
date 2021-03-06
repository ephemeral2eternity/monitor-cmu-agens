from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from datetime import date, datetime, timedelta
import time
import json
import urllib
import random
import pytz
from monitorTopology.models import *
from monitorTopology.monitor_utils import *
from monitorTopology.data_utils import *
from monitorTopology.lat_utils import *
from monitorTopology.anomalies_utils import *
from monitorTopology.dump_utils import *

# Create your views here.
# Show detailed info of all clients connecting to this agent.
def index(request):
    template = loader.get_template('monitorTopology/index.html')
    return HttpResponse(template.render({}, request))

# @description Show all sessions in the database
def showSessions(request):
    sessions = Session.objects.all()
    template = loader.get_template('monitorTopology/sessions.html')
    return HttpResponse(template.render({'sessions': sessions}, request))

# @description Show all networks in the database
def showNetworks(request):
    networks = Network.objects.all()
    template = loader.get_template('monitorTopology/networks.html')
    return HttpResponse(template.render({'networks': networks}, request))

# @description Show all ISPs discovered
def showISPs(request):
    isps = ISP.objects.all()
    peerings = PeeringEdge.objects.all()
    template = loader.get_template('monitorTopology/isps.html')
    return  HttpResponse(template.render({'isps':isps, 'peerings':peerings}, request))

# @description Show all Nodes discovered
def showNodes(request):
    nodes = Node.objects.all()
    template = loader.get_template('monitorTopology/nodes.html')
    return HttpResponse(template.render({'nodes':nodes}, request))

# @description Show all links discovered
def showLinks(request):
    links = Edge.objects.all()
    template = loader.get_template('monitorTopology/links.html')
    return HttpResponse(template.render({'links': links}, request))

# @description Show all servers discovered
def showServers(request):
    servers = Server.objects.all()
    template = loader.get_template('monitorTopology/servers.html')
    return HttpResponse(template.render({'servers':servers}, request))

def showAgents(request):
    agents = Agent.objects.all()
    template = loader.get_template('monitorTopology/agents.html')
    return HttpResponse(template.render({'agents':agents}, request))

def getSessionJson(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('client' in request_dict.keys()) and ('server' in request_dict.keys()):
        clientIP = request_dict['client'][0]
        serverIP = request_dict['server'][0]
        try:
            session = Session.objects.get(client__ip=clientIP, server__ip=serverIP)
        except:
            return JsonResponse({})
    elif ('id' in request_dict.keys()):
        try:
            session_id = int(request_dict['id'][0])
            session = Session.objects.get(id=session_id)
        except:
            return JsonResponse({})
    else:
        return JsonResponse({})

    session_json = {"id": session.id, "client": session.client.id, "server": session.server.id}
    nodes = session.route.distinct()
    nodes_list = []
    for node in nodes:
        nodes_list.append(node.id)

    nets = session.sub_networks.distinct()
    nets_list = []
    for net in nets:
        nets_list.append(net.id)

    links_list = []
    links = Edge.objects.filter(Q(src__in=session.route.distinct())&Q(dst__in=session.route.distinct())).distinct()
    for link in links:
        links_list.append(link.id)

    session_json["nodes"] = nodes_list
    session_json["networks"] = nets_list
    session_json["links"] = links_list
    rsp = JsonResponse(session_json, safe=False)
    rsp['Access-Control-Allow-Origin'] = '*'
    return rsp

# @description Get the details of one session denoted by the session id
# @called by: showSessions.
def getSession(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        session_id = int(request_dict['id'][0])
        session = Session.objects.get(id=session_id)
        hops = Hop.objects.filter(session=session)
        subnets = Subnetwork.objects.filter(session=session)
        links = Edge.objects.filter(Q(src__in=session.route.distinct())&Q(dst__in=session.route.distinct())).distinct()
        link_ids = []
        for link in links:
            link_ids.append(str(link.id))
        net_ids = []
        for net in session.sub_networks.distinct():
            net_ids.append(str(net.id))
        link_ids_str = ",".join(link_ids)
        net_ids_str = ",".join(net_ids)
        template = loader.get_template('monitorTopology/session.html')
        return HttpResponse(template.render({'session': session, 'hops': hops, 'subnets':subnets, 'edges':links,
                                             'link_ids_str':link_ids_str, 'net_ids_str':net_ids_str}, request))
    else:
        return showSessions(request)

# @description Show details of a given ISP denoted by its ASNumber (as=xxx)
def getISP(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('as' in request_dict.keys()):
        as_num = int(request_dict['as'][0])
        isp = ISP.objects.get(ASNumber=as_num)
        peerings = PeeringEdge.objects.filter(Q(srcISP__ASNumber=isp.ASNumber)|Q(dstISP__ASNumber=isp.ASNumber))
        peers = []
        for pEdge in peerings.all():
            if pEdge.srcISP.ASNumber == isp.ASNumber:
                peers.append(pEdge.dstISP)
            else:
                peers.append(pEdge.srcISP)
        template = loader.get_template('monitorTopology/isp.html')
        return HttpResponse(template.render({'isp': isp, 'peers': peers}, request))
    else:
        return HttpResponse("Please denote the AS # in http://monitor/get_isp?as=as_num!")

# @description Delete 1 isp
def deleteISP(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('as' in request_dict.keys()):
        as_num = int(request_dict['as'][0])
        isp = ISP.objects.get(ASNumber=as_num)
        isp.delete()
        return showISPs(request)
    else:
        return HttpResponse("Please denote the AS # in http://monitor/delete_isp?as=as_num!")

# @description Get the details of one node by denoting its id  in the database
def getNode(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        node_id = int(request_dict['id'][0])
        node = Node.objects.get(id=node_id)
        template = loader.get_template('monitorTopology/node.html')
        return HttpResponse(template.render({'node': node}, request))
    else:
        return HttpResponse("Please denote the node id in : http://monitor.cmu-agens.com/get_node?id=node_id")

# @description Get the details of one network by denoting its id in the database
def getNetwork(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        network_id = int(request_dict['id'][0])
        network = Network.objects.get(id=network_id)
        edges = Edge.objects.filter(Q(src__in=network.nodes.all())|Q(dst__in=network.nodes.all()))
        template = loader.get_template('monitorTopology/network.html')
        return HttpResponse(template.render({'network': network, 'edges':edges}, request))
    else:
        return showNetworks(request)

@csrf_exempt
def editNetwork(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        network_id = int(request_dict['id'][0])
        network = Network.objects.get(id=network_id)
        if request.method == "POST":
            network_info = request.POST.dict()
            # print(network_info)
            try:
                isp = ISP.objects.get(ASNumber=int(network_info['asn']))
            except:
                isp = ISP(ASNumber=int(network_info['asn']), name=network_info['isp'], type=network_info['type'])
                isp.save()

            try:
                ## Merge the network to some existing network
                new_network = Network.objects.get(isp=isp, latitude=network_info['latitude'], longitude=network_info['longitude'])
            except:
                ## Merge the existing network to a new network
                new_network = Network(isp=isp, latitude=network_info['latitude'], longitude=network_info['longitude'])
                new_network.save()

            new_network = merge_networks(network, new_network)

            new_network.city = network_info['city']
            new_network.region = network_info['region']
            new_network.country = network_info['country']
            new_network.save()

            if new_network not in isp.networks.distinct():
                isp.networks.add(new_network)
                isp.save()

            #for net in isp.networks.distinct():
            #    print(net.__str__())

            template = loader.get_template('monitorTopology/network.html')
            return HttpResponse(template.render({'network': new_network}, request))
        else:
            template = loader.get_template('monitorTopology/edit_network.html')
            return HttpResponse(template.render({'network': network}, request))
    else:
        return HttpResponse("Wrong network id denoted!")

# @description Get the specific link info
def getLink(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        link_id = int(request_dict['id'][0])
        link = Edge.objects.get(id=link_id)
        template = loader.get_template('monitorTopology/link.html')
        return HttpResponse(template.render({'link':link}, request))
    else:
        return HttpResponse("Please specify the link id in calling: /get_link?id=link_id")

# @description Get the specific server info
def getServer(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        srv_id = int(request_dict['id'][0])
        srv = Server.objects.get(id=srv_id)
    elif ('ip' in request_dict.keys):
        srv_ip = request_dict['ip'][0]
        srv = Server.objects.get(node__ip=srv_ip)
    else:
        srv = random.choice(Server.objects.all().distinct())

    template = loader.get_template('monitorTopology/server.html')
    return HttpResponse(template.render({'server':srv}, request))

# @description Get the specific link info
def getLatencyJson(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    latencies = []
    objs = []
    latencies_obj = {}
    tsExists = False
    if ('id' in request_dict.keys()) and ('type' in request_dict.keys()) and ('agent' in request_dict.keys()):
        obj_typ = request_dict['type'][0]
        agent = request_dict['agent'][0]
        ids = request_dict['id']
        tses = []

        if 'ts' in request_dict.keys():
            tsExists = True
            center_ts = float(request_dict['ts'][0])
            center_dt = datetime.datetime.utcfromtimestamp(center_ts).replace(tzinfo=pytz.utc)

        ## The obj_typ can be "link", "network" and "server"
        if obj_typ == "link":
            for obj_id in ids:
                link = Edge.objects.get(id=obj_id)
                objs.append(link)
        elif obj_typ == "session":
            for obj_id in ids:
                session = Session.objects.get(id=obj_id)
                session_links = Edge.objects.filter(Q(src__in=session.route.distinct())&Q(dst__in=session.route.distinct()))
                objs.extend(session_links)
        else:
            for obj_id in ids:
                if obj_typ == "network":
                    net = Network.objects.get(id=obj_id)
                    objs.append(net)
                else:
                    srv = Server.objects.get(id=obj_id)
                    objs.append(srv)
        for obj in objs:
            if agent == "all":
                all_latencies = obj.latencies.all()
            else:
                all_latencies = obj.latencies.filter(agent__agentType=agent)
            for lat in all_latencies:
                tses.append(lat.timestamp)
                if lat.latency > 450:
                    lat.latency = -20
                    lat.save()

                if (obj_typ == "link") or (obj_typ == "session"):
                    latencies.append({"x": lat.timestamp, "y": lat.latency, "group": obj.__str__()})
                else:
                    latencies.append({"x": lat.timestamp, "y": lat.latency, "group": obj.__str__() + "+" + lat.agent.__str__()})

        if tsExists:
            start_ts = center_dt - datetime.timedelta(minutes=5)
            end_ts = center_dt + datetime.timedelta(minutes=5)
        elif len(tses) > 0:
            start_ts = min(tses)
            end_ts = max(tses)
        else:
            end_ts = timezone.now()
            start_ts = end_ts - datetime.timedelta(minutes=5)
        latencies_obj = {"data": latencies, "start": start_ts, "end": end_ts}

        rsp = JsonResponse(latencies_obj)
        rsp['Access-Control-Allow-Origin'] = '*'
        return rsp
    else:
        return JsonResponse({})

def dumpLatencyJson(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()) and ('type' in request_dict.keys()):
        obj_typ = request_dict['type'][0]
        obj_id = request_dict['id'][0]

        ## The obj_typ can be "link", "network" and "server"
        if obj_typ == "link":
            link = Edge.objects.get(id=obj_id)
            latencies = link.latencies.all()
            lats_json = dump_lat_json(latencies)
        elif obj_typ == "session":
            session = Session.objects.get(id=obj_id)
            server = Server.objects.get(node=session.server)
            latencies = server.latencies.filter(agent__node=session.client)
            lats_json = dump_lat_json(latencies)
        else:
            net = Network.objects.get(id=obj_id)
            azure_latencies = net.latencies.filter(agent__agentType="azure")
            planetlab_latencies = net.latencies.filter(agent__agentType="planetlab")
            lats_json = {"azure":dump_lat_json(azure_latencies), "planetlab":dump_lat_json(planetlab_latencies)}

        response = HttpResponse(json.dumps(lats_json, indent=4), content_type='application/json')
        fileName = obj_typ + "_" + str(obj_id) + "_lats.json"
        response['Content-Disposition'] = 'attachment; filename="%s"' % fileName
        return response


# @description Get the count of hops for each session going through a given network denoted by id.
# @description Get network size data for all networks.
def getNetSizeJson(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        network_id = int(request_dict['id'][0])
        network = Network.objects.get(id=network_id)
        netSizeJson = network.get_network_size()
        return JsonResponse(netSizeJson)
    else:
        all_net_size = {}
        networks = Network.objects.all()
        for net in networks:
            all_net_size[net.id] = net.get_network_size()
        return JsonResponse(all_net_size)

# @description Get the network (unique AS # + locations) level topology of a network denoted by the id
def getNetworkJson(request):
    url = request.get_full_path()
    params = url.split('?')[1]
    request_dict = urllib.parse.parse_qs(params)
    if ('id' in request_dict.keys()):
        network_id = int(request_dict['id'][0])
        network = Network.objects.get(id=network_id)
        edges = Edge.objects.filter(Q(src__in=network.nodes.all())|Q(dst__in=network.nodes.all()))

        all_nodes = []
        node_list = []
        for node in network.nodes.all().distinct():
            all_nodes.append(node.ip)
            node_list.append({"name":node.name, "network_id":node.network_id, "ip":node.ip, "type": "in", "id":node.id})

        edge_list = []
        for edge in edges.all():
            if edge.src not in network.nodes.all().distinct():
                if edge.src.ip not in all_nodes:
                    all_nodes.append(edge.src.ip)
                    node_list.append({"name": edge.src.name, "network_id": edge.src.network_id, "ip": edge.src.ip, "type": "out", "id": edge.src.id})
            src_id = all_nodes.index(edge.src.ip)

            if edge.dst not in network.nodes.all():
                if edge.dst.ip not in all_nodes:
                    all_nodes.append(edge.dst.ip)
                    node_list.append({"name": edge.dst.name, "network_id": edge.dst.network_id, "ip": edge.dst.ip, "type": "out", "id": edge.dst.id})
            dst_id = all_nodes.index(edge.dst.ip)

            edge_list.append({"source":src_id, "target":dst_id})

        graph = {}
        graph["nodes"] = node_list
        graph["edges"] = edge_list

        return JsonResponse(graph)
    else:
        return JsonResponse({})

@csrf_exempt
# @description Get the router level topology json data of all sessions denoted by their ids
def getRouterGraphJson(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        if ('id' in request_dict.keys()):
            session_ids = request_dict['id']
        else:
            session_ids = [session.id for session in Session.objects.all()]
    else:
        session_ids = [session.id for session in Session.objects.all()]

    graph = get_router_graph_json(session_ids)
    return JsonResponse(graph, safe=False)

@csrf_exempt
# @description Get the network level topology json data of all sessions denoted by their ids
def getNetworkGraphJson(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        if ('id' in request_dict.keys()):
            session_ids = request_dict['id']
        else:
            session_ids = [session.id for session in Session.objects.all()]
    else:
        session_ids = [session.id for session in Session.objects.all()]

    graph = get_network_graph_json(session_ids)
    return JsonResponse(graph, safe=False)

# @description Get the network level topology of all sessions denoted by their ids
def getNetworkGraph(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        ids = request_dict['id']
        ids_json = json.dumps(ids)
    else:
        sessions = Session.objects.all()
        ids = []
        for session in sessions:
            ids.append(session.id)
        ids_json = json.dumps(ids)
    template = loader.get_template("monitorTopology/netGraph.html")
    return HttpResponse(template.render({'ids': ids_json}, request))

# @description Get the router level topology of all sessions denoted by their ids
def getRouterGraph(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        ids = request_dict['id']
        ids_json = json.dumps(ids)
    else:
        sessions = Session.objects.all()
        ids = []
        for session in sessions:
            ids.append(session.id)
        ids_json = json.dumps(ids)
    template = loader.get_template("monitorTopology/routerGraph.html")
    return HttpResponse(template.render({'ids': ids_json}, request))

def getAllISPsJson(request):
    isps = ISP.objects.all().distinct()
    all_isps = []

    for isp in isps:
        all_isps.append({"as":isp.ASNumber, "isp":isp.name, "type":isp.type, "geoCoverage":isp.get_geo_coverage(), "span":isp.get_max_span(), "size":isp.get_node_size(), "peers":isp.get_peers()})

    return JsonResponse(all_isps, safe=False)

# @description Get the peering links in json file of all isps denoted by their as numbers.
# Prepare the data for function: getISPPeering
def getISPPeersJson(request):
    url = request.get_full_path()
    isp_nets = {}
    peering_json = {}
    all_isps_related = []
    draw_all = False
    as_nums = []
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        if ('as' in request_dict.keys()):
            as_nums = request_dict['as']
            draw_all = False
        else:
            draw_all = True
    else:
        draw_all = True

    if draw_all:
        all_isps = ISP.objects.all()
        for cur_as in all_isps:
            all_isps_related.append(cur_as.name + "(AS " + str(cur_as.ASNumber) + ")")
        all_peering_links = PeeringEdge.objects.all().distinct()
    else:
        isps_to_draw = []
        for asn in as_nums:
            cur_as = ISP.objects.get(ASNumber=asn)
            isps_to_draw.append(asn)
            cur_isp_name = cur_as.name + "(AS " + str(cur_as.ASNumber) + ")"
            all_isps_related.append(cur_isp_name)

        all_peering_links = PeeringEdge.objects.filter(
            Q(srcISP__ASNumber__in=isps_to_draw) | Q(dstISP__ASNumber__in=isps_to_draw)).distinct()

        for link in all_peering_links:
            src_isp_name = link.srcISP.name + "(AS " + str(link.srcISP.ASNumber) + ")"
            dst_isp_name = link.dstISP.name + "(AS " + str(link.dstISP.ASNumber) + ")"

            if src_isp_name not in all_isps_related:
                all_isps_related.append(src_isp_name)

            if dst_isp_name not in all_isps_related:
                all_isps_related.append(dst_isp_name)

    all_isps_num = len(all_isps_related)
    peering_mat = [[0 for x in range(all_isps_num)] for y in range(all_isps_num)]
    for link in all_peering_links:
        src_isp_name = link.srcISP.name + "(AS " + str(link.srcISP.ASNumber) + ")"
        dst_isp_name = link.dstISP.name + "(AS " + str(link.dstISP.ASNumber) + ")"
        src_idx = all_isps_related.index(src_isp_name)
        dst_idx = all_isps_related.index(dst_isp_name)
        peering_mat[src_idx][dst_idx] = 1
        peering_mat[dst_idx][src_idx] = 1

        peering_json["packageNames"] = all_isps_related
        peering_json["matrix"] = peering_mat

    return JsonResponse(peering_json, safe=False)

# @description Get ISPs' networks info in json file. ISPs denoted by their AS numbers.
# Prepare the data for function: getISPMap
def getISPNetJson(request):
    url = request.get_full_path()
    isp_nets = {}
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        if ('as' in request_dict.keys()):
            as_nums = request_dict['as']
            for asn in as_nums:
                isp = ISP.objects.get(ASNumber=asn)
                isp_nets[isp.name] = []
                for net in isp.networks.distinct():
                    isp_nets[isp.name].append({"lat": net.latitude, "lon": net.longitude, "netsize": net.nodes.count(), "asn": "AS " + str(isp.ASNumber)})
    return JsonResponse(isp_nets, safe=False)

def getMapJson(request):
    servers = Server.objects.all()
    agents = Agent.objects.all()

    srv_objs = []
    for srv in servers:
        srv_objs.append({"lat": srv.node.network.latitude, "lon": srv.node.network.longitude, "name": srv.node.name, "ip": srv.node.ip, "type":"server"})

    isps = ISP.objects.all()
    isp_nets = []
    for isp in isps:
        for net in isp.networks.distinct():
            isp_nets.append({"lat": net.latitude, "lon": net.longitude, "netsize": net.nodes.count(),
                                       "asn": "AS " + str(isp.ASNumber), "type":"isp", "name":isp.name, "netID":net.id})

    agent_objs = []
    for agent in agents:
        agent_objs.append({"lat":agent.node.network.latitude, "lon":agent.node.network.longitude, "name":agent.node.name, "ip": agent.node.ip, "type":"agent"})

    map_dict = {}
    map_dict["server"] = srv_objs
    map_dict["network"] = isp_nets
    map_dict["agent"] = agent_objs

    return JsonResponse(map_dict, safe=False)


# @description Draw isps' networks in different colors on a world map
def getISPMap(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        str_ids = request_dict['as']
        ids = []
        for str_id in str_ids:
            ids.append(str_id.split("#")[1])
        ids_json = json.dumps(ids)
    else:
        isps = ISP.objects.all().distinct()
        ids = []
        for isp in isps:
            ids.append(isp.ASNumber)
        ids_json = json.dumps(ids)
    template = loader.get_template("monitorTopology/map.html")
    return HttpResponse(template.render({'ids': ids_json}, request))

# @description Draw isps' peering links in a chord graph
def getISPPeering(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        str_ids = request_dict['as']
        ids = []
        for str_id in str_ids:
            ids.append(str_id.split("#")[1])
        ids_json = json.dumps(ids)
    else:
        isps = ISP.objects.all().distinct()
        ids = []
        for isp in isps:
            ids.append(isp.ASNumber)
        ids_json = json.dumps(ids)
    template = loader.get_template("monitorTopology/ispPeeringGraph.html")
    return HttpResponse(template.render({'ids': ids_json}, request))


# @description: Get the ips to probe by the agent ip.
def getProbingIps(request):
    agent_ip = request.META['REMOTE_ADDR']
    try:
        agent = Agent.objects.get(node__ip=agent_ip)
    except:
        agent = add_agent(agent_ip)
        probe_networks()
        probe_servers()

    ips = {}
    for net in agent.networks.distinct():
        ips["network_" + str(net.id)] = [node.ip for node in net.nodes.filter(type="router").exclude(ip="*").distinct()]

    return JsonResponse(ips, safe=False)


# @description: Update all Subnetworks' hop count for all sessions going through
def updateNetSize(request):
    subnets = Subnetwork.objects.all()
    for subnet in subnets:
        subnet.update_max_hop_cnt()

    return showNetworks(request)

# @description: Update the type of all ISPs
def updateISPType(request):
    sessions = Session.objects.all().distinct()
    for session in sessions:
        client_isp = session.client.network.isp
        server_isp = session.server.network.isp
        client_isp.type = "access"
        client_isp.save()
        server_isp.type = "cloud"
        server_isp.save()

    return showISPs(request)

# @description: Update the  server objects for all server nodes
def updateServers(request):
    srv_nodes = Node.objects.filter(type="server").all()

    for srv_node in srv_nodes:
        try:
            srv = add_server(srv_node)
        except:
            print("Failed to add server for node : " + srv_node.__str__())

    return showServers(request)

# @description: Update the agent objects for all client nodes
def updateAgents(request):
    Agent.objects.all().delete()
    init_azure_nodes()
    client_nodes = Node.objects.filter(type="client").all()

    for client_node in client_nodes:
        try:
            agent = add_agent(client_node.ip)
        except:
            print("Failed to add server for node : " + client_node)

    return showAgents(request)

@csrf_exempt
def addAgent(request):
    agent_ip = request.META['REMOTE_ADDR']
    try:
        agent = add_agent(agent_ip)
    except:
        print("Failed to add agent with ip: " + agent_ip)
    return HttpResponse("Successfully add agent with ip: " + agent_ip + "!")


# @description Add the hops in the Session's route and extract the ISPs, the networks, the routers, the client
# and the server node infos.
@csrf_exempt
def addRoute(request):
    if request.method == "POST":
        ## Update the client info
        # print(request.body)
        start_time = time.time()
        route_info = json.loads(request.body.decode("utf-8"))
        #try:
        add_route(route_info)
        #except:
        #    print("Failed to add route from client " + route_info["0"]["name"])
        time_elapsed = time.time() - start_time
        print("The total time to process an add route request is : " + str(time_elapsed) + " seconds!")
        return HttpResponse("Add successfully!")
    else:
        return HttpResponse(
            "Please use the POST method for http://monitor_ip/add request to add new info for a client!")

# @description Find the closest agent in various types for all servers.
def probeServers(request):
    probe_servers()
    return showServers(request)

# @description Find the closest agent in various types for all networks.
def probeNetworks(request):
    probe_networks()
    return showNetworks(request)

# @description Report the monitored latencies to the network/server probed.
@csrf_exempt
def reportMonitoring(request):
    agent_ip = request.META['REMOTE_ADDR']
    agent = Agent.objects.get(node__ip=agent_ip)
    if request.method == "POST":
        ## Update the client info
        latency_info = json.loads(request.body.decode("utf-8"))
        ips = latency_info.keys()
        for ip in ips:
            try:
                cur_node = Node.objects.get(ip=ip)
            except:
                cur_node = add_node(ip)
            cur_lats = latency_info[ip]
            if cur_node.type == "server":
                obj = Server.objects.get(node=cur_node)
            else:
                obj = cur_node.network

            for ts in sorted(cur_lats.keys(), key=float):
                cur_dt = datetime.datetime.utcfromtimestamp(float(ts)).replace(tzinfo=pytz.utc)
                cur_lat = Latency(agent=agent, latency=float(cur_lats[ts]), timestamp=cur_dt)
                cur_lat.save()
                obj.latencies.add(cur_lat)
            obj.save()
        return HttpResponse("Report successfully from agent: " + agent_ip)
    else:
        return HttpResponse("You need to use POST method to report monitored data!")

# @description Get the network latencies mean/std by denoting the network type
def statNetLat(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        netType = request_dict['net'][0]
        agentType = request_dict['agent'][0]
    else:
        netType = "transit"
        agentType = "azure"

    networks = Network.objects.filter(isp__type=netType)

    lat_stat = []

    for net in networks:
        latencies = net.latencies.filter(agent__agentType=agentType)
        latMn, latSTD = get_lat_stat(latencies)
        lat_stat.append({"name":net.__str__(), "mean": latMn, "std":latSTD})

    lat_stat_json = {"data":lat_stat}

    return JsonResponse(lat_stat_json, safe=True)

# @description Draw bar graphs for network latencies
def drawStatNetLat(request):
    template = loader.get_template("monitorTopology/latHistogram.html")
    return HttpResponse(template.render({}, request))

# @description Draw bar graphs for network latencies
def drawStatQoEAnomalies(request):
    template = loader.get_template("monitorTopology/anomalyStats.html")
    return HttpResponse(template.render({}, request))

# @description Draw bar graphs for network latencies
def scatterOriginAnomalisJson(request):
    origin_anomalies_json = get_scatter_origin_anomalies_json()
    return JsonResponse(origin_anomalies_json, safe=False)

# @description Draw bar graphs for network latencies
def scatterISP(request):
    template = loader.get_template("monitorTopology/ispScatter.html")
    return HttpResponse(template.render({}, request))

# @description Draw bar graphs for network latencies
def scatterNetworks(request):
    template = loader.get_template("monitorTopology/scatterNetworks.html")
    return HttpResponse(template.render({}, request))

# @description Show details of all anomalies in table
def showAllAnomalies(request):
    anomalies = Anomaly.objects.all()
    severe_anomalies = anomalies.filter(type="severe")
    severe_sessions = get_anomalous_sesssions(severe_anomalies)
    medium_anomalies = anomalies.filter(type="medium")
    medium_sessions = get_anomalous_sesssions(medium_anomalies)
    light_anomalies = anomalies.filter(type="light")
    light_sessions = get_anomalous_sesssions(light_anomalies)
    template = loader.get_template("monitorTopology/anomalies.html")
    return HttpResponse(template.render({'anomalies': anomalies,
                                         "severe":severe_anomalies, "medium":medium_anomalies, "light":light_anomalies,
                                         "severe_sessions":severe_sessions, "medium_sessions":medium_sessions, "light_sessions":light_sessions}, request))

# @description Delete all anomalies in the database
def delAllAnomalies(request):
    anomalies = Anomaly.objects.all().delete()
    return HttpResponse("Successfully empty the anomaly database!")

def getAnomaly(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        anomaly_id = request_dict['id'][0]
        anomaly = Anomaly.objects.get(id=anomaly_id)
        hops = Hop.objects.filter(session=anomaly.session)
        links = Edge.objects.filter(
            Q(src__in=anomaly.session.route.distinct()) & Q(dst__in=anomaly.session.route.distinct())).distinct()
        link_ids = []
        for link in links:
            link_ids.append(str(link.id))
        net_ids = []
        for net in anomaly.session.sub_networks.distinct():
            net_ids.append(str(net.id))
        link_ids_str = ",".join(link_ids)
        net_ids_str = ",".join(net_ids)

        template = loader.get_template("monitorTopology/anomaly.html")
        return HttpResponse(template.render({'anomaly': anomaly, 'hops':hops,
                                             'link_ids_str':link_ids_str, 'net_ids_str': net_ids_str},request))
    else:
        return HttpResponse("Please specify anomaly id when calling http://monitor/get_anomaly?id=anomaly_id")

def showQoEs(request):
    qoes = QoE.objects.all().order_by('-timestamp')[:100]
    template = loader.get_template("monitorTopology/recent_qoes.html")
    return HttpResponse(template.render({'qoes': qoes}, request))

def cacheAllQoEs(request):
    cache_all_qoes()
    return HttpResponse("Successfully cache all QoE values locally!")

def cacheAllAnomalies(request):
    cache_all_qoe_anomalies()
    return showAllAnomalies(request)

def getAnomaliesPerSessionsJson(request):
    anomalies_per_sessions = getAnomaliesPerSessions()
    return JsonResponse(anomalies_per_sessions, safe=False)

def getAnomaliesPerOriginJson(request):
    anomalies_per_origins = getAnomaliesPerOrigins()
    return JsonResponse(anomalies_per_origins, safe=False)

def dumpAllAnomaliesJson(request):
    anomalies_json = dump_all_anomalies_json()
    response = HttpResponse(json.dumps(anomalies_json, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="anomalies.json"'
    return response

def dumpAllISPsJson(request):
    isps_json = dump_all_isps_json()
    response = HttpResponse(json.dumps(isps_json, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="isps.json"'
    return response

def dumpAllNetworksJson(request):
    nets_json = dump_all_networks_json()
    response = HttpResponse(json.dumps(nets_json, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="networks.json"'
    return response

def dumpAllSessionsJson(request):
    sessions_json = dump_all_sessions_json()
    response = HttpResponse(json.dumps(sessions_json, sort_keys=True, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="sessions.json"'
    return response

def dumpAllNodesJson(request):
    nodes_json = dump_all_nodes_json()
    response = HttpResponse(json.dumps(nodes_json, sort_keys=True, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="nodes.json"'
    return response

def dumpAllLinksJson(request):
    links_json = dump_all_links_json()
    response = HttpResponse(json.dumps(links_json, sort_keys=True, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="links.json"'
    return response
