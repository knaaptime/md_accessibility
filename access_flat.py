
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import pandana as pdna
import geopandas as gpd

# In[2]:

print "reading shape data"

gdf = gpd.GeoDataFrame.from_file('input/dmv_lehd_2010_adjusted.shp')



gdf['geom_old']= gdf['geometry']
gdf['geometry'] = gdf['geometry'].centroid


# In[4]:


gdf.head(5)

print "...done"


# In[5]:

x, y = zip(*[(p.x, p.y) for (i, p) 
             in gdf.geometry.iteritems()])
x = pd.Series(x)
y = pd.Series(y)


print "reading network data and precomputing impedance"


# In[6]:

store = pd.HDFStore('input/osm_md.h5', "r")
nodes = store.nodes
edges = store.edges
print nodes.head(3)
print edges.head(3)



net=pdna.Network(nodes.x, 
                       nodes.y, 
                       edges["from"], 
                       edges.to, 
                       edges[["weight"]])
net.precompute(8000)


# In[8]:

net.init_pois(num_categories=1, max_dist=8000, max_pois=1000)


print "...done"

# In[9]:

net.set_pois("blocks", x, y)


# In[10]:

node_ids = net.get_node_ids(x, y)


# In[11]:

net.set(node_ids, variable=gdf.TOTAL, name="jobs")
net.set(node_ids, variable=gdf.POP10, name="labor")



print "calculating accessibility"
# In[12]:

print "15 min"

w_labor_15 = net.aggregate(1250, type="sum", decay="flat", name="labor")


w_jobs_15 = net.aggregate(1250, type="sum", decay="flat", name="jobs")

print "30 min"

w_jobs_30 = net.aggregate(2500, type="sum", decay="flat", name="jobs")
w_labor_30 = net.aggregate(2500, type="sum", decay="flat", name="labor")

print "45 min walk and bike"

w_jobs_45 = net.aggregate(3200, type="sum", decay="flat", name="jobs")

w_labor_45 = net.aggregate(3200, type="sum", decay="flat", name="labor")

b_jobs_45 = net.aggregate(7000, type="sum", decay="flat", name="jobs")

b_labor_45 = net.aggregate(7000, type="sum", decay="flat", name="labor")

print "...done."

print "building dataframes"


# In[13]:

gdf["node_ids"] = net.get_node_ids(x, y)
gdf['geometry'] = gdf['geom_old']
gdf.drop('geom_old', axis=1, inplace=True)



# In[14]:

w_labor_15.name = "w_labor_15"
w_jobs_15.name = "w_jobs_15"

w_labor_30.name = "w_labor_30"
w_jobs_30.name = "w_jobs_30"

w_labor_45.name = "w_labor_45"
b_labor_45.name = "b_labor_45"
w_jobs_45.name = "w_jobs_45"
b_jobs_45.name = "b_jobs_45"



# In[16]:

w_jobs_45 = pd.DataFrame(w_jobs_45)
w_labor_45 = pd.DataFrame(w_labor_45)
b_jobs_45 = pd.DataFrame(b_jobs_45)
b_labor_45 = pd.DataFrame(b_labor_45)

w_jobs_15 = pd.DataFrame(w_jobs_15)
w_labor_15 = pd.DataFrame(w_labor_15)
w_jobs_30 = pd.DataFrame(w_jobs_30)
w_labor_30 = pd.DataFrame(w_labor_30)


# In[18]:

access = w_jobs_15.join([w_labor_15, w_jobs_30, w_labor_30, w_jobs_45, w_labor_45, b_jobs_45, b_labor_45])


# In[19]:

print "writing csv"


# In[20]:

access.to_csv('output/accessibility_flat.csv')

print "...done"

# In[21]:

test = gdf.join(access, on="node_ids")


# In[22]:

test.drop('w_geocode', axis=1, inplace=True)


# In[23]:

test2 = gpd.GeoDataFrame(test)



# In[29]:

test2 = test2.query("STATEFP10 == '24'")

print "writing shapefile"

# In[30]:

test2.to_file('output/dmv_accessibility_flat.shp')


print "...done. Script Complete"

# In[1]:

# test2.to_file(filename='/Users/knaaptime/GIS/accessibility/dmv_access_v4.geojson', driver='GeoJSON')





