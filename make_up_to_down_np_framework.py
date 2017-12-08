# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:08:42 2017

@author: RHill04
"""
import os
import sys
import pysal as ps
import numpy as np
import pandas as pd
from collections import deque, defaultdict, OrderedDict
from scipy import ndimage

ctl_path = 'D:/WorkFolder/WetConnect_Nov2016/Scripts/WetConnScripts'
#ctl_path = 'J:/GitProjects/Wetland Connectivity/WetlandScripts/'

#sys.path.append(ctl_path)  
#from WetCat_functions import dbf2DF
def dbf2DF(dbfile, upper=True):
    '''
    __author__ = "Ryan Hill <hill.ryan@epa.gov>"
                 "Marc Weber <weber.marc@epa.gov>"
    Reads and converts a dbf file to a pandas data frame using pysal.

    Arguments
    ---------
    dbfile           : a dbase (.dbf) file
    '''
    db = ps.open(dbfile)
    cols = {col: db.by_col(col) for col in db.header}
    db.close()  #Close dbf 
    pandasDF = pd.DataFrame(cols)
    if upper == True:
        pandasDF.columns = pandasDF.columns.str.upper() 
    return pandasDF

year = '2011'
nhddir = "L:/Priv/CORFiles/Geospatial_Library/Data/RESOURCE/PHYSICAL/HYDROLOGY/NHDPlusV21"
working_dir = 'D:/WorkFolder/WetConnect_Nov2016'
frmto_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/WetlandPath/FlowTables/'
streamlink_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/WetlandPath/CostPaths/'
numpy_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/WetlandPath/WetPaths_npy/'

inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
          
for region in inputs.keys():
    for hydro in inputs[region]:
        print 'Region ' + region + ' and hydro number ' + hydro
        for dirs in os.listdir(nhddir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                rpu =  dirs[-3:]
                print rpu
                start_time = time.time()
                streamlink = dbf2DF(streamlink_dir + 'StreamLink_' + rpu + '.tif.vat.dbf')
                streamlink = np.array(streamlink.VALUE)
                
                flow = dbf2DF(frmto_dir+'/WetlandFrmTo' + rpu + '.dbf')
                t = np.array(flow.FLOWTOFINA)
                f = np.array(flow.STREAMLINK)

                down = np.unique(t, return_counts=True)
                lengths = down[1]
                down = down[0]
  
                unq = np.unique(np.append(f,t))
                seq = np.repeat(np.NAN, len(unq))
                ids = unq[np.where(np.in1d(unq,t, invert=True))] 
                
                path_add = np.array([0])          
                i = 1                 
                while len(path_add) != 0:
                    seq[np.in1d(unq,ids)] = i
                    test = np.in1d(f, ids)  
                    path_add = down[ndimage.sum(test, t, down) == lengths] 
                    ids = np.append(ids, path_add)
                    rm = f[np.in1d(t, path_add)]
                    ids = np.setdiff1d(ids, rm)
                    i = i + 1
                
                down = np.repeat(np.NAN, len(unq)) 
                down[np.searchsorted(unq,f)] = t    
                
                if not os.path.exists(numpy_dir + 'updown_framework'):
                    os.makedirs(numpy_dir + 'updown_framework')    
                
                np.save(numpy_dir + 'updown_framework/down_' + rpu + '.npy', down)
                np.save(numpy_dir + 'updown_framework/seq_' + rpu + '.npy', seq)
                np.save(numpy_dir + 'updown_framework/unq_' + rpu + '.npy', unq)  
                print("--- %s seconds ---" % (time.time() - start_time))    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    