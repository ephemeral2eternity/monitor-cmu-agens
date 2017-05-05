from django.conf.urls import url
from monitorTopology import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_route$', views.addRoute, name='addRoute'),
    url(r'^add_agent$', views.addAgent, name='addAgent'),
    url(r'^report$', views.reportMonitoring, name='reportMonitoring'),
    url(r'^update_net_size', views.updateNetSize, name='updateNetSize'),
    url(r'^update_isp_type', views.updateISPType, name='updateISPType'),
    url(r'^update_servers', views.updateServers, name='updateServers'),
    url(r'^update_agents', views.updateAgents, name='updateAgents'),
    url(r'^probe_servers', views.probeServers, name='probeServers'),
    url(r'^probe_networks', views.probeNetworks, name='probeNetworks'),
    url(r'^show_sessions', views.showSessions, name='showSessions'),
    url(r'^show_networks', views.showNetworks, name='showNetworks'),
    url(r'^show_links', views.showLinks, name='showLinks'),
    url(r'^show_isps', views.showISPs, name='showISPs'),
    url(r'^show_nodes', views.showNodes, name='showNodes'),
    url(r'^show_servers', views.showServers, name='showServers'),
    url(r'^show_agents', views.showAgents, name='showAgents'),
    url(r'^get_all_isps_json', views.getAllISPsJson, name='getAllISPsJson'),
    url(r'^get_isp_nets_json', views.getISPNetJson, name='getISPNetJson'),
    url(r'^get_map_json', views.getMapJson, name='getMapJson'),
    url(r'^get_isp_peers_json', views.getISPPeersJson, name='getISPPeersJson'),
    url(r'^get_isp_peering', views.getISPPeering, name='getISPPeering'),
    url(r'^get_isp_map', views.getISPMap, name='getISPMap'),
    url(r'^get_isp', views.getISP, name='getISP'),
    url(r'^del_isp', views.deleteISP, name='deleteISP'),
    url(r'^get_session_json', views.getSessionsJson, name='getSessionsJson'),
    url(r'^get_session', views.getSession, name='getSession'),
    url(r'^get_node', views.getNode, name='getNode'),
    url(r'^get_latency_json', views.getLatencyJson, name='getLinkLatencyJson'),
    url(r'^get_link', views.getLink, name='getLink'),
    url(r'^get_server', views.getServer, name='getServer'),
    url(r'^get_net_size_json$', views.getNetSizeJson, name='getNetSizeJson'),
    url(r'^get_network$', views.getNetwork, name='getNetwork'),
    url(r'^edit_network', views.editNetwork, name='editNetwork'),
    url(r'^get_network_json$', views.getNetworkJson, name='getNetworkJson'),
    url(r'^get_router_graph_json', views.getRouterGraphJson, name='getRouterGraphJson'),
    url(r'^get_router_graph', views.getRouterGraph, name='getRouterGraph'),
    url(r'^get_net_graph_json', views.getNetworkGraphJson, name='getNetworkGraphJson'),
    url(r'^get_net_graph', views.getNetworkGraph, name='getNetworkGraph'),
    url(r'^get_probing_ips', views.getProbingIps, name='getProbingIps'),
    url(r'^stat_net_lat', views.statNetLat, name='statNetLat'),
    url(r'^cache_all_anomalies', views.cacheAllAnomalies, name='cacheAllAnomalies'),
    url(r'^show_anomalies', views.showAllAnomalies, name='showAllAnomalies'),
    url(r'^del_anomalies', views.delAllAnomalies, name='delAllAnomalies'),
    url(r'^get_anomaly', views.getAnomaly, name='getAnomaly'),
    url(r'^get_anomalies_per_session_json', views.getAnomaliesPerSessionsJson, name='statQoEAnomaliesJson'),
    url(r'^get_anomalies_per_origin_json', views.getAnomaliesPerOriginJson, name='statQoEAnomaliesJson'),
    url(r'^scatter_origin_anomalies_json', views.scatterOriginAnomalisJson, name='scatterOriginAnomalisJson'),
    url(r'^scatter_isps', views.scatterISP, name='scatterISP'),
    url(r'^scatter_networks', views.scatterNetworks, name='scatterNetworks'),
    url(r'^draw_stat_qoe_anomalies', views.drawStatQoEAnomalies, name='drawStatQoEAnomalies'),
    url(r'^draw_stat_net_lat', views.drawStatNetLat, name='drawStatNetLat'),
]