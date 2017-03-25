import json
import requests
import os
import socket
import struct
from urllib import request

## host2ip
# Change the hostname to ip address
def host2ip(hop_name):
    try:
        ip = socket.gethostbyname(hop_name)
    except socket.error:
        # print "[Error]The hostname : ", hop_name, " can not be resolved!"
        ip = "*"
    return ip

## is_reserved
# TO check if the given ip is reserved as private addresses
def is_reserved(ip):
    f = struct.unpack('!I', socket.inet_aton(ip))[0]
    private = (
        [2130706432, 4278190080], # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
        [3232235520, 4294901760], # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
        [2886729728, 4293918720], # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
        [167772160,  4278190080], # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
    )
    for net in private:
        if (f & net[1]) == net[0]:
            return True
    return False

## ipinfo
# Use commercial API http://ipinfo.io/ to obtain the AS #, ISP, hostname, geolocation information of a given IP
def ipinfo(ip=None):
    if ip:
        url = 'http://ipinfo.io/' + ip
    else:
        url = 'http://ipinfo.io/'

    hop_info = {}
    try:
        resp = requests.get(url)
        hop_info = json.loads(resp.text)
    except:
        print("[Error]Failed to get hop info from ipinfo.io, the maximum # of requests have been achieved today!")
        print("[Error]The ip needed is :" + ip)
        exit(0)

    if 'org' in hop_info.keys():
        hop_org = hop_info['org']
        hop_org_items = hop_org.split()
        hop_info['AS'] = int(hop_org_items[0][2:])
        hop_info['ISP'] = " ".join(hop_org_items[1:])
    else:
        hop_info['AS'] = -1
        hop_info['ISP'] = "unknown"

    if 'loc' in hop_info.keys():
        locations = hop_info['loc'].split(',')
        hop_info['latitude'] = float(locations[0])
        hop_info['longitude'] = float(locations[1])
    else:
        hop_info['latitude'] = 0.0
        hop_info['longitude'] = 0.0

    if ('city' not in hop_info.keys()):
        hop_info['city'] = ''

    if ('region' not in hop_info.keys()):
        hop_info['region'] = ''

    if ('country' not in hop_info.keys()):
        hop_info['country'] = ''

    if ('hostname' not in hop_info.keys()):
        hop_info['hostname'] = ip
    elif ('No' in hop_info['hostname']):
        hop_info['hostname'] = ip

    hop_info['name'] = hop_info['hostname']

    return hop_info

#########################################################################
## Obtain node info from our centralized manager's database
## manager: manager ip address
## ip: the ip of the node to be retrieved
## @return: the node info json dict
#########################################################################
def get_node_info_from_manager(manager, ip=None, nodeType="router"):
    if ip:
        url = 'http://%s/nodeinfo/get_node?ip=%s' % (manager, ip)
    else:
        url = 'http://%s/nodeinfo/get_node' % manager

    try:
        resp = requests.get(url)
        node_info = json.loads(resp.text)
        if node_info:
            obtained = True
        else:
            obtained = False
    except:
        if ip:
            node_info = ipinfo(ip)
        else:
            node_info = ipinfo()
        node_info['type'] = nodeType

        post_node_info_to_manager(manager, node_info)

    return node_info

##########################################################################
## Post node info to the centralized manager
## manager: manager ip address
## ip: the ip of the node to be retrieved
## @return: the node info json dict
#########################################################################
def post_node_info_to_manager(manager, node_info):
    url = 'http://%s/nodeinfo/add_node' % manager
    isSuccess = True
    try:
        req = request.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = request.urlopen(req, json.dumps(node_info))
    except:
        isSuccess = False

    return isSuccess

#########################################################################
## get_node_info
# Obtain an ip's info by either our own service or ipinfo service
#########################################################################
def get_node_info(ip=None, nodeTyp='router'):
    manager = "manage.cmu-agens.com"
    node_info = get_node_info_from_manager(manager, ip, nodeTyp)
    return node_info

if __name__ == "__main__":
    ip = "207.210.142.101"
    ip_info = get_node_info(ip, "router")
    print(ip_info)