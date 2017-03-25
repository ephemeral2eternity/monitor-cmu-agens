from django.conf.urls import url
from monitorTopology import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^add_route$', views.addRoute, name='addRoute'),
    url(r'^show_sessions', views.showSessions, name='showSessions'),
    url(r'^get_session', views.getSession, name='getSession'),
    url(r'^get_router_graph_json', views.getRouterGraphJson, name='getRouterGraphJson'),
    url(r'^get_router_graph', views.getRouterGraph, name='getRouterGraph'),
    url(r'^get_net_graph_json', views.getNetworkGraphJson, name='getNetworkGraphJson'),
    url(r'^get_net_graph', views.getNetworkGraph, name='getNetworkGraph'),
]