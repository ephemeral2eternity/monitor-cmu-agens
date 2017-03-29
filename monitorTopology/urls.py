from django.conf.urls import url
from monitorTopology import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_route$', views.addRoute, name='addRoute'),
    url(r'^update_net_size', views.updateNetSize, name='updateNetSize'),
    url(r'^update_isp_type', views.updateISPType, name='updateISPType'),
    url(r'^show_sessions', views.showSessions, name='showSessions'),
    url(r'^show_networks', views.showNetworks, name='showNetworks'),
    url(r'^get_isp_nets_json', views.getISPNetJson, name='getISPNetJson'),
    url(r'^get_isp_peers_json', views.getISPPeersJson, name='getISPPeersJson'),
    url(r'^get_isp_peering', views.getISPPeering, name='getISPPeering'),
    url(r'^get_isp_map', views.getISPMap, name='getISPMap'),
    url(r'^show_isps', views.showISPs, name='showISPs'),
    url(r'^show_nodes', views.showNodes, name='showNodes'),
    url(r'^get_isp', views.getISP, name='getISP'),
    url(r'^get_session', views.getSession, name='getSession'),
    url(r'^get_node', views.getNode, name='getNode'),
    url(r'^get_net_size_json$', views.getNetSizeJson, name='getNetSizeJson'),
    url(r'^get_network$', views.getNetwork, name='getNetwork'),
    url(r'^get_network_json$', views.getNetworkJson, name='getNetworkJson'),
    url(r'^get_router_graph_json', views.getRouterGraphJson, name='getRouterGraphJson'),
    url(r'^get_router_graph', views.getRouterGraph, name='getRouterGraph'),
    url(r'^get_net_graph_json', views.getNetworkGraphJson, name='getNetworkGraphJson'),
    url(r'^get_net_graph', views.getNetworkGraph, name='getNetworkGraph'),
]