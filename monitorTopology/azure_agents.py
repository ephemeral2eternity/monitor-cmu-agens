from azure.common.credentials import UserPassCredentials
from azure.mgmt.compute import ComputeManagementClient
# from azure.mgmt.compute import ComputeManagementClient, ComputeManagementClientConfiguration
from azure.mgmt.network import NetworkManagementClient
# from azure.mgmt.network import NetworkManagementClient, NetworkManagementClientConfiguration
import json
import os

def list_azure_agents(rg_name, prefix):
    info_dict = json.load(open(os.path.dirname(__file__) + "/info.json"))
    # info_dict = json.load(open(os.getcwd() + "/info.json"))
    # location_dict = json.load(open(os.getcwd() + "/locations.json"))
    subscription_id = info_dict["subscription_id"]
    # TODO: See above how to get a Credentials instance
    credentials = UserPassCredentials(
        info_dict["user"],    # Your new user
        info_dict["password"],  # Your password, Woku5113
    )

    #compute_client = ComputeManagementClient(ComputeManagementClientConfiguration(
    #        credentials,
    #        subscription_id
    #    )
    #)

    compute_client = ComputeManagementClient(credentials, subscription_id)

    #network_client = NetworkManagementClient(NetworkManagementClientConfiguration(
    #        credentials,
    #        subscription_id
    #    )
    #)

    network_client = NetworkManagementClient(credentials, subscription_id)

    agents = []

    vms = compute_client.virtual_machines.list(rg_name)
    for vm in vms:
        vm_name = vm.name
        # print(vm_name)
        if prefix in vm_name:
            vm_ip = network_client.public_ip_addresses.get(rg_name, vm_name+"-ip").ip_address
            vm_location = vm.location
            print(vm_name, vm_ip, vm_location)
            cur_agent = {"name" : vm_name, "ip" : vm_ip, "location" : vm_location}
            agents.append(cur_agent)


    return agents

def list_locators(rg_name, prefix):
    info_dict = json.load(open(os.path.dirname(__file__) + "/info.json"))
    # info_dict = json.load(open(os.getcwd() + "/info.json"))
    subscription_id = info_dict["subscription_id"]
    # TODO: See above how to get a Credentials instance
    credentials = UserPassCredentials(
        info_dict["user"],    # Your new user
        info_dict["password"],  # Your password, Woku5113
    )

    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    agents = []

    vms = compute_client.virtual_machines.list(rg_name)
    for vm in vms:
        vm_name = vm.name
        if prefix in vm_name:
            vm_ip = network_client.public_ip_addresses.get(rg_name, vm_name).ip_address
            vm_location = vm.location
            print(vm_name, vm_ip, vm_location)
            cur_agent = {"name" : vm_name, "ip" : vm_ip, "location" : vm_location}
            agents.append(cur_agent)


    return agents

if __name__ == '__main__':
    agents = list_azure_agents("monitoring", "agent-")
    print(agents)
    locators = list_locators("agens", "locator-")
    print(locators)
