import requests
import datetime
import json
import sys
import pytz
from monitorTopology.azure_agents import *
from monitorTopology.models import Anomaly, Cause, Session, Network, Server

#####################################################################################
## @params: locator_ip ---- the ip of the locator to get the anomalies data.
##          ts ---- the timestamp from which the anomalies to be retrieved
## @return: nodes_json ---- the json object that contains info for all nodes
#####################################################################################
def get_qoe_anomalies(locator_ip, ts=None):
    if ts:
        url = "http://%s/diag/get_all_anomalies_json?ts=%s" % (locator_ip, ts)
    else:
        url = "http://%s/diag/get_all_anomalies_json" % locator_ip
    try:
        rsp = requests.get(url)
        return rsp.json()
    except:
        return []

#####################################################################################
## @descr: collect QoE anomalies from all locators
#####################################################################################
def get_all_qoe_anomalies():
    locators = list_locators("agens", "locator-")

    all_anomalies = []
    for locator in locators:
        locator_ip = locator["ip"]
        locator_name = locator["name"]
        print("Getting QoE anomalies from locator: " + locator_name)
        if Anomaly.objects.filter(locator=locator_name).count() > 0:
            ts = Anomaly.objects.filter(locator=locator_name).latest(field_name="timestamp").timestamp.timestamp()
            qoe_anomalies = get_qoe_anomalies(locator_ip, ts)
        else:
            qoe_anomalies = get_qoe_anomalies(locator_ip)
        all_anomalies.extend(qoe_anomalies)
    return all_anomalies

#####################################################################################
## @descr: Cache all data obtained to database
#####################################################################################
def cache_all_qoe_anomalies():
    all_anomalies = get_all_qoe_anomalies()
    for anomaly_dict in all_anomalies:
        client = anomaly_dict["client"]
        server = anomaly_dict["server"]
        ts = anomaly_dict["timestamp"]
        try:
            anomaly_dt = datetime.datetime.utcfromtimestamp(float(ts)).replace(tzinfo=pytz.utc)
            anomalous_session = Session.objects.get(client__ip=client, server__ip=server)
            # print(anomalous_session.__str__())
            anomaly = Anomaly(locator=anomaly_dict["locator"],
                              lid=int(anomaly_dict["lid"]), session_lid=int(anomaly_dict["session_lid"]),
                              type=anomaly_dict["type"], session=anomalous_session,
                              timeToDiagnose=anomaly_dict["timeToDiagnose"], timestamp=anomaly_dt)
            anomaly.save()
            # print(anomaly_dict)
            for cause_dict in anomaly_dict["causes"]:
                print(cause_dict)
                cause_origin_type = cause_dict["type"]
                obj_mid = -1
                if cause_origin_type == "network":
                    try:
                        net_origin = Network.objects.get(isp__ASNumber=int(cause_dict["as"]),
                                                         latitude=cause_dict["latitude"],
                                                         longitude=cause_dict["longitude"])
                        obj_mid = net_origin.id
                    except:
                        print("No network with AS: " + cause_dict["as"] + " at (" + cause_dict["latitude"] + ", "
                              + cause_dict["longitude"] + ") found in monitor database!")
                elif cause_origin_type == "server":
                    try:
                        server_origin = Server.objects.get(node__ip=cause_dict["ip"])
                        obj_mid = server_origin.id
                    except:
                        print("No server with ip: " + cause_dict["ip"] + " found in monitor database")

                print("Saving cause_dict!")
                cause = Cause(type=cause_dict["type"], obj_lid=cause_dict["lid"], obj_mid=obj_mid,
                              count=cause_dict["count"], data=json.dumps(cause_dict, indent=4))
                cause.save()
                anomaly.origins.add(cause)
            anomaly.save()
        except ValueError as e:
            print(e.__str__())
            continue
        except TypeError as e:
            print(e.__str__())
            continue
        except:
            # print("Cannot cache anomaly with client " + client + " server " + server + " as no database record for the session found!")
            print("Unexpected error:", sys.exc_info()[0])
            print(anomaly_dict)
            continue

#####################################################################################
## @descr: Get all anomalies session ids
## @params: anomalies ---- the anomalies given to get the anomalous sessions
#####################################################################################
def get_anomalous_sesssions(anomalies):
    anomalous_sessions = []
    for anomaly in anomalies.all():
        if anomaly.session not in anomalous_sessions:
            anomalous_sessions.append(anomaly.session)

    return anomalous_sessions

#####################################################################################
## @descr: Get the anomalies per session id
## @return: session_anomalies ---- Get the anomalies id and type per session.
#####################################################################################
def getAnomaliesPerSessions():
    anomalies = Anomaly.objects.all()

    session_anomalies = {}
    for anomaly in anomalies:
        session_id = anomaly.session.id
        if session_id not in session_anomalies.keys():
            session_anomalies[session_id] = {"severe":[], "medium":[], "light":[]}

        session_anomalies[session_id][anomaly.type].append(anomaly.id)

    return session_anomalies

#####################################################################################
## @descr: Get the anomalies per session id
## @return: session_anomalies ---- Get the anomalies id and type per session.
#####################################################################################
def getAnomaliesCntPerSessions(session_anomalies):
    anomaly_cnt_per_session = {"session":[], "severe":[], "medium":[], "light":[]}

    for session_id in sorted(session_anomalies.keys(), key=int):
        anomaly_cnt_per_session["session"].append(session_id)
        anomaly_cnt_per_session["severe"].append(len(session_anomalies[session_id]["severe"]))
        anomaly_cnt_per_session["medium"].append(len(session_anomalies[session_id]["medium"]))
        anomaly_cnt_per_session["light"].append(len(session_anomalies[session_id]["light"]))

    return anomaly_cnt_per_session

# @descr: Get the anomaly counts per ISP, Networks, Nodes in different types
def getAnomaliesPerOrigins():
    anomalies = Anomaly.objects.all()

    isp_anomalies = {
        "cloud":{},
        "transit":{},
        "access":{}
    }

    net_anomalies = {
        "cloud":{},
        "transit":{},
        "access":{}
    }

    node_anomalies = {
        "server":{},
        "client":{}
    }

    for anomaly in anomalies:
        for origin in anomaly.origins.all():
            if origin.type == "server":
                srv = origin.get_cause_obj()
                if srv.node.ip not in node_anomalies["server"].keys():
                    node_anomalies["server"][srv.node.ip] = []
                node_anomalies["server"][srv.node.ip].append({"type": anomaly.type, "count":origin.count, "id":anomaly.id})

            if origin.type == "device":
                client = anomaly.session.client
                if client.ip not in node_anomalies["client"].keys():
                    node_anomalies["client"][client.ip] = []
                node_anomalies["client"][client.ip].append(
                    {"type": anomaly.type, "count": origin.count, "id": anomaly.id})

            if origin.type == "network":
                net = origin.get_cause_obj()
                if net.id not in net_anomalies[net.isp.type].keys():
                    net_anomalies[net.isp.type][net.id] = []
                net_anomalies[net.isp.type][net.id].append({"type": anomaly.type, "count":origin.count, "id":anomaly.id})

                if net.isp.ASNumber not in isp_anomalies[net.isp.type].keys():
                    isp_anomalies[net.isp.type][net.isp.ASNumber] = []
                isp_anomalies[net.isp.type][net.isp.ASNumber].append({"type": anomaly.type, "count":origin.count, "id":anomaly.id})

    anomalies_per_origins = {"isps":isp_anomalies, "networks":net_anomalies, "nodes":node_anomalies}
    return anomalies_per_origins


if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    all_anomalies = get_all_qoe_anomalies()
    print(all_anomalies)