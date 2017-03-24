from django.db import models

# Create your models here.
# Node class defines a node that is either a router, or a client , or a server
class Node(models.Model):
    name = models.CharField(max_length=500)
    ip = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100)
    network = models.ForeignKey('Network', blank=True)
    # node_qoe_score = models.DecimalField(default=5, max_digits=5, decimal_places=4)
    related_sessions = models.ManyToManyField('Session')
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type + ":" + self.ip

    def get_class_name(self):
        return "node"

class ISP(models.Model):
    ASNumber = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500, default="")
    networks = models.ManyToManyField("Network", through="Network", blank=True)

    def __str__(self):
        return "AS " + str(self.ASNumber) + "(" + self.name + ")"

    # Network defines a network that several routers in an end-to-end delivery path belongs to
class Network(models.Model):
    type = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    nodes = models.ManyToManyField(Node, blank=True, related_name='net_nodes')
    # network_qoe_score = models.DecimalField(default=5, max_digits=5, decimal_places=4)
    related_sessions = models.ManyToManyField('Session')
    city = models.CharField(max_length=100, default="")
    region = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=100, default="")
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type + ", AS " + str(self.ASNumber) + ", (" + str(self.latitude) + ", " + str(
            self.longitude) + ")"

    class Meta:
        index_together = ["ASNumber", "latitude", "longitude"]
        unique_together = ("ASNumber", "latitude", "longitude")

    def get_class_name(self):
        return "network"

## Session information
class Session(models.Model):
    src = models.ForeignKey(Node, related_name='src_node')
    dst = models.ForeignKey(Node, related_name='dst_node')
    route = models.ManyToManyField(Node, through='Hop')
    sub_networks = models.ManyToManyField(Network, through='Subnetwork')
    latest_check = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client.name + "<-->" + self.server.name

    def get_class_name(self):
        return "session"

    class Meta:
        index_together = ["src", "dst"]
        unique_together = ["src", "dst"]

# Define hop with its sequence on a client's route
class Hop(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    hopID = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.hopID) + ", " + str(self.node) + ", " + str(self.session)

# Define hop with its sequence on a client's route
class Subnetwork(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    netID = models.PositiveIntegerField()

    def __str__(self):
        return str(self.netID) + ", " + str(self.network) + ", " + str(self.session)

class Edge(models.Model):
    src = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='node_source')
    dst = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='node_target')
    isIntra = models.BooleanField(default=False)
    latencies = models.ManyToManyField("LinkLatency", through="LinkLatency")

    latest_check = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["src", "dst"]

    def __str__(self):
        return str(self.src.name + "---" + self.dst.name)


class NetEdge(models.Model):
    srcNet = models.ForeignKey(Network, related_name='network_source')
    dstNet = models.ForeignKey(Network, related_name='network_target')
    isIntra = models.BooleanField(default=False)

    class Meta:
        unique_together = ["srcNet", "dstNet"]

    def __str__(self):
        return str(self.srcNet) + "---" + str(self.dstNet)

class LinkLatency(models.Model):
    link = models.ForeignKey(Edge)
    latency = models.DecimalField()
    timestamp = models.DateTimeField()

class AgentLatency(models.Model):
    agent = models.ForeignKey(Node)
    latency = models.DecimalField()
    timestamp = models.DateTimeField()