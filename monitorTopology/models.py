from django.db import models

# Create your models here.
# Node class defines a node that is either a router, or a client , or a server
class Node(models.Model):
    name = models.CharField(max_length=500)
    ip = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    network = models.ForeignKey('Network')
    # node_qoe_score = models.DecimalField(default=5, max_digits=5, decimal_places=4)
    related_sessions = models.ManyToManyField('Session', through="Hop", blank=True)
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type + ":" + self.ip

    class Meta:
        index_together = ["network", "ip"]
        unique_together = ["network", "ip"]

    def get_class_name(self):
        return "node"

# Server class that includes a server node and all latencies measured on the server
class Server(models.Model):
    node = models.ForeignKey(Node)
    latencies = models.ManyToManyField("Latency", blank=True)
    agents = models.ManyToManyField('Agent', blank=True, through="ServerProbing")

    def __str__(self):
        return self.node.__str__()

    def get_class_name(self):
        return "server"

# Agent class that denotes the agent to probe a network or a server.
class Agent(models.Model):
    node = models.ForeignKey(Node)
    agentType = models.CharField(max_length=100)
    servers = models.ManyToManyField(Server, blank=True, through="ServerProbing")
    networks = models.ManyToManyField("Network", blank=True, through="NetProbing")

    def __str__(self):
        return self.agentType + ":" + self.node.name + "@(" + str(self.node.network.latitude) + "," + str(self.node.network.longitude) + ")"

    def get_class_name(self):
        return "agent"


class ISP(models.Model):
    ASNumber = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500, default="")
    networks = models.ManyToManyField("Network", blank=True, related_name="isp_nets")
    type = models.CharField(max_length=100, default="transit")

    def __str__(self):
        return "AS " + str(self.ASNumber) + "(" + self.name + ")"

    def get_class_name(self):
        return "isp"

    def get_size(self):
        isp_size = 0
        for network in self.networks.all().distinct():
            isp_size += network.get_max_size()
        return isp_size

# Network defines a network that several routers in an end-to-end delivery path belongs to
class Network(models.Model):
    isp = models.ForeignKey(ISP, related_name="net_isp")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    nodes = models.ManyToManyField(Node, blank=True, related_name='net_nodes')
    # network_qoe_score = models.DecimalField(default=5, max_digits=5, decimal_places=4)
    related_sessions = models.ManyToManyField('Session', through="Subnetwork", blank=True)
    latencies = models.ManyToManyField("Latency", blank=True)
    agents = models.ManyToManyField("Agent", blank=True, through="NetProbing")
    city = models.CharField(max_length=100, default="")
    region = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=100, default="")
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "AS " + str(self.isp.ASNumber) + ", (" + str(self.latitude) + ", " + str(
            self.longitude) + ")"

    class Meta:
        index_together = ["isp", "latitude", "longitude"]
        unique_together = ("isp", "latitude", "longitude")

    def get_class_name(self):
        return "network"

    # Count all session's hops through this network
    def get_network_size(self):
        net_size = {}
        subnets = Subnetwork.objects.filter(network=self).all().distinct()
        for subnet in subnets:
            net_size[subnet.session.id] = subnet.maxHopSize
        return net_size

    def get_max_size(self):
        all_size = self.get_network_size()
        if all_size:
            max_size = max(all_size.values())
        else:
            max_size = -1
        return max_size


## Session information
class Session(models.Model):
    client = models.ForeignKey(Node, related_name='client_node')
    server = models.ForeignKey(Node, related_name='server_node')
    route = models.ManyToManyField(Node, through='Hop', blank=True)
    sub_networks = models.ManyToManyField(Network, through='Subnetwork', blank=True)
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client.name + "<-->" + self.server.name

    def get_class_name(self):
        return "session"

    ## Get the maximum route length
    def get_max_route_len(self):
        minHopCnt = 30
        maxHopCnt = 0
        hops = Hop.objects.filter(session=self).all()
        for hop in hops.distinct():
            if hop.hopID < minHopCnt:
                minHopCnt = hop.hopID
            if hop.hopID > maxHopCnt:
                maxHopCnt = hop.hopID

        max_route_len = maxHopCnt - minHopCnt + 1
        return max_route_len

    ## Get the count of unique networks the session goes through
    def get_net_cnt(self):
        return self.sub_networks.all().distinct().count()

    ## Get the count of unique isps the session goes through
    def get_isp_cnt(self):
        isp_as = []
        for net in self.sub_networks.all().distinct():
            if net.isp.ASNumber not in isp_as:
                isp_as.append(net.isp.ASNumber)
        return len(isp_as)


    class Meta:
        index_together = ["client", "server"]
        unique_together = ["client", "server"]

# Define hop with its sequence on a client's route
class Hop(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    hopID = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.hopID) + ", " + str(self.node) + ", " + str(self.session)

    class Meta:
        index_together = ["session", "node", "hopID"]
        unique_together = ["session", "node", "hopID"]

# Define hop with its sequence on a client's route
class Subnetwork(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    netID = models.PositiveIntegerField()
    maxHopSize = models.IntegerField(default=-1)

    def __str__(self):
        return str(self.netID) + ", " + str(self.network) + ", " + str(self.session)

    class Meta:
        index_together = ["session", "network", "netID"]
        unique_together = ["session", "network", "netID"]

    def update_max_hop_cnt(self):
        minHopCnt = 30
        maxHopCnt = 0
        hops = Hop.objects.filter(node__in=self.network.nodes.all(), session=self.session).all()
        for hop in hops.distinct():
            if hop.hopID < minHopCnt:
                minHopCnt = hop.hopID
            if hop.hopID > maxHopCnt:
                maxHopCnt = hop.hopID

        self.maxHopSize = maxHopCnt - minHopCnt + 1
        self.save()
        return self.maxHopSize

# Define the pair of agent and network to denote which agent is probing which network.
class NetProbing(models.Model):
    network = models.ForeignKey(Network)
    agent = models.ForeignKey(Agent)

    def __str__(self):
        return self.agent.__str__() + " probing " + self.network.__str__()

# Define the pair of agent and network to denote which agent is probing which network.
class ServerProbing(models.Model):
    server = models.ForeignKey(Server)
    agent = models.ForeignKey(Agent)

    def __str__(self):
        return self.agent.__str__() + " probing " + self.server.__str__()

# Define the edge between two nodes.
class Edge(models.Model):
    src = models.ForeignKey(Node, related_name='node_source')
    dst = models.ForeignKey(Node, related_name='node_target')
    isIntra = models.BooleanField(default=False)
    latencies = models.ManyToManyField("Latency", blank=True)

    latest_check = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["src", "dst"]

    def __str__(self):
        return str(self.src.name + "<--->" + self.dst.name)

class NetEdge(models.Model):
    srcNet = models.ForeignKey(Network, related_name='net_src')
    dstNet = models.ForeignKey(Network, related_name='net_dst')
    isIntra = models.BooleanField(default=False)

    latest_check = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = ["srcNet", "dstNet"]
        unique_together = ["srcNet", "dstNet"]

    def __str__(self):
        return str(self.srcNet) + "<--->" + str(self.dstNet)

class PeeringEdge(models.Model):
    srcISP= models.ForeignKey(ISP, related_name='isp_source')
    dstISP = models.ForeignKey(ISP, related_name='isp_target')

    class Meta:
        unique_together = ["srcISP", "dstISP"]

    def __str__(self):
        return str(self.srcISP) + "<--->" + str(self.dstISP)

class Latency(models.Model):
    agent = models.ForeignKey(Agent, default=None, null=True)
    latency = models.DecimalField(decimal_places=4, max_digits=10)
    timestamp = models.DateTimeField()
