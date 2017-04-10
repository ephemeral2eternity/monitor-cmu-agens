import requests
import time
import json
from monitorTopology.azure_agents import *

def get_qoe_anomalies(locator_ip):
    url = "http://%s/diag/get_classified_anomalies_json" % locator_ip
    try:
        rsp = requests.get(url)
        return rsp.json()
    except:
        return {}

## @ Collect all QoE anomalies from all locators
def get_all_qoe_anomalies():
    curfilePath = os.path.abspath(__file__)
    curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))  # this will return current directory in which python file resides.
    parentDir = os.path.abspath(os.path.join(curDir, os.pardir))  # this will return parent directory.
    outputJsonName = "anomalies_" + time.strftime("%m%d") + ".json"

    if os.path.exists(parentDir + "/databackup/" + outputJsonName):
        with open(parentDir + "/databackup/" + outputJsonName) as json_data:
            merged_anomalies = json.load(json_data)
            return merged_anomalies

    locators = list_locators("agens", "locator-")

    all_anomalies = {}
    for locator in locators:
        locator_ip = locator["ip"]
        locator_name = locator["name"]
        print("Getting QoE anomalies from locator: " + locator_name)
        qoe_anomalies = get_qoe_anomalies(locator_ip)
        all_anomalies[locator_name] = qoe_anomalies

    ## Merge all locators' data
    merged_anomalies = {}
    for locator in all_anomalies.keys():
        # print("Merging anomalies from locator: " + locator)
        locator_anomalies = all_anomalies[locator]
        for origin_type in locator_anomalies.keys():
            origin_anomalies = locator_anomalies[origin_type]
            if origin_type not in merged_anomalies.keys():
                merged_anomalies[origin_type] = {}
            for origin in origin_anomalies.keys():
                if origin not in merged_anomalies[origin_type].keys():
                    merged_anomalies[origin_type][origin] = []
                merged_anomalies[origin_type][origin].extend(locator_anomalies[origin_type][origin])

    with open(parentDir + "/databackup/" + outputJsonName, "w") as outFile:
        json.dump(merged_anomalies, outFile, sort_keys=True, indent=4, ensure_ascii=True)

    return merged_anomalies

if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    all_anomalies = get_all_qoe_anomalies()
    print(all_anomalies["transitISP"])