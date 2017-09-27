# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 14:39:15 2017

@author: Rdebbout
"""
import numpy as np
import pandas as pd
import sys
sys.path.append('D:/Projects/StreamCat')
from StreamCat_functions import Accumulation, appendConnectors, interVPU

npy = 'D:/NHDPlusV21/StreamCat_npy'
inputs = np.load('%s/zoneInputs.npy' % npy).item()
home = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Allocation_Accumulation'
ftn = 'WetlandMag'
accum_type = 'Categorical'
Connector = "%s/%s_connectors.csv" % (home, ftn)  # File string to store InterVPUs needed for adjustments

interVPUtbl = pd.read_csv('D:/Projects/StreamCat/InterVPU.csv')


for zone in inputs:
    print zone
    #break
    cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))    
    if zone in interVPUtbl.ToZone.values:
        cat = appendConnectors(cat, Connector, zone, interVPUtbl)    
    accum = np.load('%s/bastards/accum_%s.npz' % (npy ,zone))
    up = Accumulation(cat, accum['comids'], 
                           accum['lengths'], 
                           accum['upstream'], 
                           'UpCat')
    accum = np.load('%s/children/accum_%s.npz' % (npy ,zone))
    ws = Accumulation(cat, accum['comids'],
                           accum['lengths'],
                           accum['upstream'],
                           'Ws')
    if zone in interVPUtbl.ToZone.values:
        cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))
    if zone in interVPUtbl.FromZone.values:
        interVPU(ws, cat.columns[1:], accum_type, zone, 
                 Connector, interVPUtbl.copy(), None)
    upFinal = pd.merge(up, ws, on='COMID')
    final = pd.merge(cat, upFinal, on='COMID')
    final.fillna(0, inplace=True)
    final.to_csv('%s/%s_%s.csv' % (home, ftn, zone), index=False)
    
    
###############################################################################
# add missing COMIDs from StreamCat so all tables have proper length for accum
   
alloc = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/Allocation_and_Accumulation'
 
for zone in inputs:
    print zone
    cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))
    sc = pd.read_csv('%s/Clay_%s.csv' % (alloc, zone))[['COMID']]
    tbl = pd.merge(cat,sc,on='COMID',how='right').fillna(0)
    tbl.to_csv('%s/%s_%s.csv' % (home, ftn, zone),index=False)
    
