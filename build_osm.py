from pandana.loaders import osm

print "loading network from OSM"
network = osm.network_from_bbox(37.8856, -79.4872, 39.7905, -74.9852, network_type='walk', two_way=True)

print "removing disconnected subgraphs"
lcn = network.low_connectivity_nodes(10000, 10, imp_name='distance')

print "saving network to HDF5"
network.save_hdf5('input/osmnetwork.h5', rm_nodes=lcn)

print "done"
