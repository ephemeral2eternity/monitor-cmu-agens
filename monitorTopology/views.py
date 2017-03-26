from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from datetime import date, datetime, timedelta
import time
import json
import urllib
from monitorTopology.monitor_utils import *
from monitorTopology.data_utils import *

# Create your views here.
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

def showNodes(request):
    nodes = Node.objects.all()
    template = loader.get_template('monitorTopology/nodes.html')
    return HttpResponse(template.render({'nodes':nodes}, request))

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
        template = loader.get_template('monitorTopology/session.html')
        return HttpResponse(template.render({'session': session, 'hops': hops, 'subnets':subnets}, request))
    else:
        return showSessions(request)

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

# @description Get the details of one node by denoting its id in the database
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

# @description Get the router topology of a network denoted by the id
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


def getISPGraph(request):
    url = request.get_full_path()
    if '?' in url:
        params = url.split('?')[1]
        request_dict = urllib.parse.parse_qs(params)
        ids = request_dict['id']
        ids_json = json.dumps(ids)
    else:
        isps = ISP.objects.all().distinct()
        ids = []
        for isp in isps:
            ids.append(isp.ASNumber)
        ids_json = json.dumps(ids)
    template = loader.get_template("monitorTopology/ispGraph.html")
    return HttpResponse(template.render({'ids': ids_json}, request))


# @description Add the hops in the Session's route and extract the ISPs, the networks, the routers, the client
# and the server node infos.
@csrf_exempt
def addRoute(request):
    if request.method == "POST":
        ## Update the client info
        # print(request.body)
        start_time = time.time()
        route_info = json.loads(request.body.decode("utf-8"))
        try:
            add_route(route_info)
        except:
            print("Faiiled to add route from client " + route_info["0"]["name"])
        time_elapsed = time.time() - start_time
        print("The total time to process an add route request is : " + str(time_elapsed) + " seconds!")
        return HttpResponse("Add successfully!")
    else:
        return HttpResponse(
            "Please use the POST method for http://monitor_ip/add request to add new info for a client!")