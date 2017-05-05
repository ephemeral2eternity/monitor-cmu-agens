from django.db.models import Q
from monitorTopology.models import Anomaly, Cause, Network, Server, Session, Hop, Edge, Latency

def get_session_json():
    sessions = Session.objects.all()

    sessions_json = {}
    for session in sessions:
        sessions_json[session.id] = {"client":session.client.id, "server":session.server.id}

        hops_dict = {}
        hops = Hop.objects.filter(session=session)
        for hop in hops:
            if hop.hopID not in hops_dict.keys():
                hops_dict[hop.hopID] = []
            hops_dict[hop.hopID].append(hop.node.id)
        links = Edge.objects.filter(Q(src__in=session.route.distinct())&Q(dst__in=session.route.distinct()))
        links_dict = {}
        for link in links:
            links_dict[link.id] = {"isIntra": link.isIntra, "src":link.src.id, "dst":link.dst.id}

        sessions_json[session.id]["hops"] = hops_dict
        sessions_json[session.id]["links"] = links_dict

        lats_dict = {}
        server = Server.objects.get(node=session.server)
        session_lats = server.latencies.filter(agent__node=session.client)

        for lat in session_lats.all():
            lats_dict[lat.timestamp.timestamp()] = lat.latency

        sessions_json[session.id]["latencies"] = lats_dict

    return sessions_json

# if __name__ == '__main__':
    #locator_ip = "13.93.223.198"
    #qoe_anomalies = get_qoe_anomalies(locator_ip)
    #print(qoe_anomalies)
    # all_anomalies = get_all_qoe_anomalies()
    # print(all_anomalies)