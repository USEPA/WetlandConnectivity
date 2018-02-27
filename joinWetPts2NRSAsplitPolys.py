# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:44:35 2017

@author: Rdebbout
"""

import os
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
    
home = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity'
        '/SpatialDataInputs/Wetlands_NLCD2011/WetlandPoints')

pol = gpd.read_file(('L:/Priv/CORFiles/Geospatial_Library/Data/Project'
                     '/WetlandConnectivity/NitrogenModeling/NRSA_Polys'
                     '/NRSA_split_polys_0809.shp'))

tbl = pd.read_csv('D:/Projects/NRSA0809/runStreamCat/cbnf.csv')[['SITE_ID',
                                                                 'CAT_COMID']]
pol.merge(tbl,on='SITE_ID')

jtbl = pd.DataFrame()
for f in os.listdir(home):
    if '.shp' in f and not 'lock' in f:
        print f
        t = gpd.read_file('%s/%s' % (home,f))
        t.to_crs(pol.crs,inplace=True)
        tbl = sjoin(pol,t)
        print len(tbl)
        if len(tbl) > 0:
            tbl = tbl[['SITE_ID','CAT_COMID','GRID_CODE']]
            jtbl = pd.concat([jtbl,tbl])

jtbl.to_csv(('L:/Priv/CORFiles/Geospatial_Library/Data/Project/'
            'WetlandConnectivity/NitrogenModeling/'
            'join_nrsa_wet.csv'),index=False)