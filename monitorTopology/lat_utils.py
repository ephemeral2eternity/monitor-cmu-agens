from monitorTopology.models import Latency
import numpy

### @function get_lat_stat(latencies)
#   @descrip
#   @params:
#       latencies : the queryset of latencies
#   @return: lat_mn ---- the mean value of latencies
#            lat_std ---- the standard deviation of latencies
def get_lat_stat(latencies):
    lat_list = []
    for lat in latencies.all().order_by('-timestamp'):
        lat_list.append(lat.latency)

    lat_mn = numpy.mean(lat_list)
    lat_std = numpy.std(lat_list)

    return lat_mn, lat_std

