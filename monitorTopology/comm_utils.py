import requests
import time
import json
from monitorTopology.azure_agents import *
from monitorTopology.models import Anomaly, Cause

def get_qoe_anomalies(locator_ip):
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
        qoe_anomalies = get_qoe_anomalies(locator_ip)
        all_anomalies.extend(qoe_anomalies)
    return all_anomalies

'''
def cache_all_qoe_anomalies():
    all_anomalies = get_all_qoe_anomalies()
    for anomaly_dict in all_anomalies:
'''

if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    all_anomalies = get_all_qoe_anomalies()
    print(all_anomalies)