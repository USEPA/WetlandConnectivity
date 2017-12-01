# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 14:39:15 2017

@author: Rdebbout
"""

###############################################################################
# Accumulate VPU zonal tables for UpCat and Ws stats.

import numpy as np
import pandas as pd
import sys
sys.path.append('D:/Projects/StreamCat')
from StreamCat_functions import Accumulation, appendConnectors, interVPU

npy = 'D:/NHDPlusV21/StreamCat_npy'
inputs = np.load('%s/zoneInputs.npy' % npy).item()
home = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity'
        '/NitrogenModeling/Allocation_Accumulation')
accum_type = 'Categorical'
interVPUtbl = pd.read_csv('D:/Projects/StreamCat/InterVPU.csv')

ftn = 'WetlandFreq'
Connector = "%s/%s_connectors.csv" % (home, ftn)  # File string to store InterVPUs needed for adjustments

for zone in inputs:
    print zone
    #break
    cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))   
    if zone in interVPUtbl.ToZone.values:
        cat = appendConnectors(cat, Connector, zone, interVPUtbl)    
    accum = np.load('%s/bastards/accum_%s.npz' % (npy ,zone))
    if not len(cat) == len(accum['comids']): 
    # this will assume that any COMID not in the cat csv has 0 WetDrainArea
        register = pd.DataFrame({'COMID':accum['comids']}) 
        cat = pd.merge(register, cat, how='left', on='COMID').fillna(0)
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
# Fold together split-cat tables of just Catchment stats with upstream (UpCat)
# and calcutlate Ws stats for NRSA sites.

import numpy as np
import pandas as pd

spot = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/'
        'WetlandConnectivity/NitrogenModeling')

names = ['WetlandType','WetlandFreq','WetlandMag','WetlandMagAvg',
         'WetlandDist','WetDrainManure','WetDrainFert',
         'WetDrainCMAQ','WetDrainCbnf']

inputs = ['06','05','10U','10L','07','11','14','01','17','16','15',
          '13','12','09','02','08','04','03W','03S','03N','18']

for name in names:
    print name
    final = pd.read_csv('%s/splitMetrics/%s.csv' % (spot,name))
    addAll = pd.DataFrame()
    for zone in inputs:
        add = pd.read_csv('%s/Allocation_Accumulation/%s_%s.csv' % (spot,
                                                                    name,
                                                                    zone))
        add = add.ix[add.COMID.isin(final.CAT_COMID)]
        columns = [x for x in add.columns if 'Up' in x]
        add = add[['COMID'] + columns]
        addAll = pd.concat([addAll,add])            
    both = pd.merge(final,addAll,
                    left_on='CAT_COMID',
                    right_on='COMID',
                    how='left')
    both.drop('COMID',axis=1,inplace=True)
    both.rename(columns={'CAT_COMID':'COMID'}, inplace=True)
    cats = [col for col in both.columns if col[:3] == 'Cat']
    for x in cats:
        both['Ws' + x[3:]] = both[x] + both['UpCat' + x[3:]]        
    both.to_csv('%s/NRSA_Results/%s.csv' % (spot,name),index=False)
