import requests
import datetime
import json
import sys
import pytz
from monitorTopology.azure_agents import *
from monitorTopology.models import Anomaly, Cause, Session, Network, Server

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

## @ Collect all QoE anomalies from all locators
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

## Cache all data obtained to database
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

if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    all_anomalies = get_all_qoe_anomalies()
    print(all_anomalies)