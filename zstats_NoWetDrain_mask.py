# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 10:06:42 2017

Run the NoWetDrain masked catchments to be accumulated with
the accumulate4StreamCat script.

@author: Rdebbout
"""

import os
import arcpy
import numpy as np
import pandas as pd
import sys
sys.path.append('D:/Projects/StreamCat')
from StreamCat_functions import dbf2DF
from arcpy.sa import ZonalStatisticsAsTable
arcpy.CheckOutExtension("spatial")

home = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling'
layers = ['cbnf','manure',]
lr_dir = '%s/LandscapeRasters' % home
z_dir = '%s/LandscapeRasters/WetlandNoWetDrainMask/gridcoded' % home
out_dir = '%s/Allocation_Accumulation/DBF_stash' % home
npy = 'D:/NHDPlusV21/StreamCat_npy'
inputs = np.load('%s/zoneInputs.npy' % npy).item()
rpus = np.load('%s/rpuInputs.npy' % npy).item()
arcpy.env.cellSize = "30"

for lyr in layers:
    print lyr
    vallyr = '%s/%s.tif' % (lr_dir,lyr)
    for zone in inputs:
        pre = 'D:/NHDPlusV21/NHDPlus%s/NHDPlus%s' % (inputs[zone], zone)
        tbl = pd.DataFrame()
        for rpu in rpus[zone]:
            inZoneData = '%s/WetCat_GRID_%s.tif' % (z_dir, rpu)
            arcpy.env.snapRaster = inZoneData
            out = '%s/zstats_%s_%s.dbf' % (out_dir,lyr,rpu)
            if not os.path.exists(out):
                ZonalStatisticsAsTable(inZoneData, 'VALUE', vallyr, out, "DATA", "ALL")
            tbl = pd.concat([tbl,dbf2DF(out)])        
        zn = dbf2DF('%s/NHDPlusCatchment/Catchment.dbf' % pre)[['GRIDCODE','FEATUREID']]
        t = pd.merge(zn,tbl,left_on='GRIDCODE',right_on='VALUE',how='left')
        t['AreaSqKm'] = t.AREA * 1e-6
        t = t[['FEATUREID','AreaSqKm','COUNT','SUM']].fillna(0)
        t.columns = ['COMID','CatAreaSqKm','CatCount','CatSum']
        t.to_csv('%s/Allocation_Accumulation/NoWet_%s_%s.csv' % (home,lyr,zone),index=False)
        
for f in os.listdir(out_dir):
    if '.xml' in f or '.cpg' in f:
        os.remove('%s/%s' % (out_dir,f))