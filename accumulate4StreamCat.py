# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 14:39:15 2017
This script takes the output from 'WetlandResultProcessingForStreamCat.Rmd'
and accumulates upstream and watershed metrics based off of the catchment stats
produced in those output tables.

@author: Rdebbout
"""

###############################################################################
# Accumulate VPU zonal tables for UpCat and Ws stats.

import numpy as np
import pandas as pd
import sys
sys.path.append('D:/Projects/StreamCat')
from StreamCat_functions import appendConnectors, interVPU

npy = 'D:/NHDPlusV21/StreamCat_npy'
inputs = np.load('%s/zoneInputs.npy' % npy).item()
home = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity'
        '/NitrogenModeling/Allocation_Accumulation')
accum_type = 'Categorical'
interVPUtbl = pd.read_csv('D:/Projects/StreamCat/InterVPU.csv')

metrics = ['WetDrainCbnf','WetDrainManure','WetDrainFert','WetDrainCMAQ','WetDrainPointN']

for ftn in metrics:
    print ftn
    Connector = "%s/%s_connectors.csv" % (home, ftn)  # File string to store InterVPUs needed for adjustments
    for zone in inputs:
        print zone
#        break
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
# and calculate Ws stats for NRSA sites.

import numpy as np
import pandas as pd

spot = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/'
        'WetlandConnectivity/NitrogenModeling')

names = ['WetlandType','WetlandFreq','WetlandMag','WetlandMagAvg',
         'WetlandDist','WetDrainManure','WetDrainFert',
         'WetDrainCMAQ','WetDrainCbnf']

names = ['WetDrainManure','WetDrainFert',
         'WetDrainCMAQ','WetDrainCbnf', 'WetDrainPointN'] #

inputs = ['06','05','10U','10L','07','11','14','01','17','16','15',
          '13','12','09','02','08','04','03W','03S','03N','18']

a_w_cols = ['CatCMAQ','CatCbnf','CatFert','CatManure']

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
                    how='left').fillna(0)
    both.drop('COMID',axis=1,inplace=True)
    both.rename(columns={'CAT_COMID':'COMID'}, inplace=True)
    cols = [col for col in both.columns if col[:3] == 'Cat']
    for col in cols:
        if col in a_w_cols:
           both['Ws' + col[3:]] = ((both[col] * both.CatDrainAreaSqKm) + 
                                   (both['UpCat' + col[3:]] * both.UpCatDrainAreaSqKm)
                                  )/(both.CatDrainAreaSqKm + both.UpCatDrainAreaSqKm)
        else:
            both['Ws' + col[3:]] = both[col] + both['UpCat' + col[3:]]
    both.to_csv('%s/NRSA_Results/%s.csv' % (spot,name),index=False)



# the accumulation function can't currently handle tables w/o 'AreaSqKM
ftn= 'N_wetland_mitigated_freq1'
for zone in inputs:
    print zone
    cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))
    cat['AreaSqKm'] = 0
    cat.to_csv('%s/%s_%s.csv' % (home, ftn, zone),index=False)
    
for zone in inputs:
    print zone
    cat = pd.read_csv('%s/%s_%s.csv' % (home, ftn, zone))
    cols = [col for col in cat.columns if not 'AreaSqKm' in col]
    cat = cat[cols]
    cat.to_csv('%s/%s_%s.csv' % (home, ftn, zone),index=False)
    
####################################################################
scat = 
for zone in inputs:
    print zone
    f = '%s/RD/WetDrainCMAQ_%s.csv' % (home, zone)
    a = pd.read_csv(f)
    b = pd.read_csv('%s/WetDrainCbnf_%s.csv' % (home, zone))
    c = pd.merge(a,b[['COMID']],how='right',on='COMID').fillna(0)
    c.to_csv(f,index=False)

####################################################################
    
def swapper(coms, upStream):
    '''
    __author__ =  "Marc Weber <weber.marc@epa.gov>"
                  "Ryan Hill <hill.ryan@epa.gov>"
    Creates array of indexes for all upstream COMIDs that will be summarized for each local catchment.

    Arguments
    ---------
    coms                  : numpy array of all COMIDs in the zone
    upstream              : numpy array of all upstream COMIDs for each local catchment
    '''
    bsort = np.argsort(coms)
    apos = np.searchsorted(coms[bsort], upStream)
    indices = bsort[apos]
    return indices    
 
def Accumulation(arr, COMIDs, lengths, upStream, tbl_type, icol='COMID'):
    '''
    __author__ =  "Marc Weber <weber.marc@epa.gov>" 
                  "Ryan Hill <hill.ryan@epa.gov>"
    Uses the 'Cat' and 'UpCat' columns to caluculate watershed values and returns those values in 'Cat' columns 
	so they can be appended to 'CatResult' tables in other zones before accumulation.

    Arguments
    ---------
    arr                   : table containing watershed values
    COMIDs                : numpy array of all zones COMIDs
    lengths               : numpy array with lengths of upstream COMIDs
    upstream              : numpy array of all upstream arrays for each COMID
    tbl_type              : string value of table metrics to be returned
    icol                  : column in arr object to index
    '''
    coms = np.array(arr[icol])  #Read in COMIDs
    indices = swapper(coms, upStream)  #Get indices that will be used to map values
    del upStream  # a and indices are big - clean up to minimize RAM
    cols = arr.columns[1:]  #Get column names that will be accumulated
    z = np.zeros(COMIDs.shape)  #Make empty vector for placing values
    outT = np.zeros((len(COMIDs), len(arr.columns)))  #Make empty array for placing final values
    outT[:,0] = COMIDs  #Define first column as comids
    #Loop and accumulate values
    for k in range(0,len(cols)):
        col = cols[k]
        c = np.array(arr[col]) # arr[col].fillna(0) keep out zeros where no data!
        d = c[indices] #Make final vector from desired data (c)
        if col in ['CatCMAQ','CatCbnf','CatFert','CatManure']:
            area = np.array(arr.ix[:, 1])
            ar = area[indices]
            x = 0
            for i in range(0, len(lengths)):
                # using nan_to_num in average function to treat NA's as zeros when summing
                z[i] = np.ma.average(np.nan_to_num(d[x:x + lengths[i]]), weights=ar[x:x + lengths[i]])
                x = x + lengths[i]
        else:
            x = 0
            for i in range(0, len(lengths)):
                z[i] = np.nansum(d[x:x + lengths[i]])
                x = x + lengths[i]
        outT[:,k+1] = z  #np.nan_to_num() -used to convert to zeros here, now done above in the np.ma.average()
    outT = outT[np.in1d(outT[:,0], coms),:]  #Remove the extra COMIDs
    outDF = pd.DataFrame(outT)
    if tbl_type == 'Ws':
        outDF.columns = np.append(icol, map(lambda x : x.replace('Cat', 'Ws'),cols.values))
    if tbl_type == 'UpCat':
        outDF.columns = np.append(icol, 'Up' + cols.values)
#    for name in outDF.columns:
#        if 'AreaSqKm' in name:
#            areaName = name
#    outDF.loc[(outDF[areaName] == 0), outDF.columns[2:]] = np.nan  # identifies that there is no area in catchment mask, then NA values across the table   
    return outDF    
    

