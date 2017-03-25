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


# @description Add the hops in the Session's route and extract the ISPs, the networks, the routers, the client
# and the server node infos.
@csrf_exempt
def addRoute(request):
    if request.method == "POST":
        ## Update the client info
        # print(request.body)
        start_time = time.time()
        route_info = json.loads(request.body.decode("utf-8"))
        add_route(route_info)
        time_elapsed = time.time() - start_time
        print("The total time to process an add route request is : " + str(time_elapsed) + " seconds!")
        return HttpResponse("Add successfully!")
    else:
        return HttpResponse(
            "Please use the POST method for http://monitor_ip/add request to add new info for a client!")