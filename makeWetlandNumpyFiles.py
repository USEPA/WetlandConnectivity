# -*- coding: utf-8 -*-
"""
Created on Tue Jun 07 10:13:51 2016

@author: RHill04
"""

import os, sys
import pysal as ps
import numpy as np
from collections import deque, defaultdict, OrderedDict

numpy_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/WetPath_npy/'
path_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/FlowTables/'
link_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Data/'
    
    #Need to set to where WetCat_function.py is stored
wetcatfunc = 'D:/WorkFolder/WetlandConnectivity/'
sys.path.append(wetcatfunc)  
from WetCat_functions import dbf2DF, children, bastards

files = filter(lambda x: x.endswith(('.dbf')) and not x.count('.tif'), os.listdir(path_dir))

for file in files:
        #Read in wetland paths to get list of COMIDs
    strlink_dbf = link_dir + 'StreamLink' + file[-7:-4] + '.tif.vat.dbf'
    tbl = dbf2DF(strlink_dbf)
    COMIDs = tbl.VALUE.values        
        #Read in from-to table
    flow = dbf2DF(path_dir + file)[[1,2]] #Only need columns 1 and 2
    print "Processing region: " + file[-7:-4] + " with total records = " + str(len(flow))
    flow.columns = ['TOCOMID','FROMCOMID'] #Rename columns
    flow  = flow[flow.FROMCOMID != 0] #Remove paths with FROMCOMID == 0
    fromID = np.array(flow.FROMCOMID) #Make numpy arrays of from and to columns
    toID = np.array(flow.TOCOMID)
        #Make dictionary of next downpath ID
    DownCOMs = defaultdict(list)
    for i in range(0, len(flow), 1):
        FROMID = fromID[i]
        TOID = toID[i]
        DownCOMs[FROMID].append(TOID)                              
        
        #Make and save bastards
    a = map(lambda x: bastards(x, DownCOMs), COMIDs) #Make bastards vector
    lengths = np.array([len(v) for v in a]) #Make lengths vector
    a = np.int32(np.hstack(np.array(a)))    #Convert to 1d vector
    np.save(numpy_dir + 'bastards/downPath' + file[-7:-4] + '.npy', a)
    np.save(numpy_dir + 'bastards/comids' + file[-7:-4] + '.npy', COMIDs)
    np.save(numpy_dir + 'bastards/lengths' + file[-7:-4] + '.npy', lengths)
    
         #Make and save children
    a = map(lambda x: children(x, DownCOMs), COMIDs) #Make children vector
    lengths = np.array([len(v) for v in a]) #Make lengths vector
    a = np.int32(np.hstack(np.array(a)))    #Convert to 1d vector
    np.save(numpy_dir + 'children/downPath' + file[-7:-4] + '.npy', a)
    np.save(numpy_dir + 'children/comids' + file[-7:-4] + '.npy', COMIDs)
    np.save(numpy_dir + 'children/lengths' + file[-7:-4] + '.npy', lengths)   
    
