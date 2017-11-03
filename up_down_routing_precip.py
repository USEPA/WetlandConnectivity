# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 14:30:29 2017

@author: RHill04
"""
import glob, os
import numpy as np
import pandas as pd
from scipy import ndimage
import time

year = '2011'
numpy_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/WetlandPath/WetPaths_npy/updown_framework/'
vars_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Incremental_N_Inputs/'

test = os.listdir(numpy_dir)
test = filter(lambda k: 'unq' in k, test)
start_time = time.time()
for i in test:
    
    print i
    suffix =  i[len('unq_'):]
    rpu = suffix[:len('.npy')-1]
        #Load numpy arrays
    unq = np.load(numpy_dir + i) 
    down = np.load(numpy_dir + 'down_' + suffix) 
    seq = np.load(numpy_dir + 'seq_' + suffix) 
        #Read in precip table
    mod_inputs_x = pd.read_csv(vars_dir + 'Precip2Yr24hr_' + rpu + '.csv')
    mod_inputs = mod_inputs_x.dropna(axis=0)
        #Pull out pathids, areas, and precip (mm)
    pathid = np.int64(np.array(mod_inputs.PATHID))
    matcher0 = np.in1d(pathid, unq)
    pathid = pathid[matcher0]
    areacol = np.array(mod_inputs.WETCAT_AREA)
    precipcol = np.array(mod_inputs.PRECIP_2YR24HR_MM)
    areacol = areacol[matcher0]
    precipcol = precipcol[matcher0]
    
    order = np.searchsorted(unq, pathid)
    val = np.repeat(0., len(unq))
    area = np.repeat(np.NAN, len(unq))
    precip = np.repeat(np.NAN, len(unq))
    
    area[order] = areacol
    precip[order] = precipcol
    
    for k in np.unique(seq):

        matcher = np.in1d(seq, k)
        t_unq = unq[matcher]
        t_down = down[matcher]
        t_d_unq = np.unique(t_down)  
        
        t_area = area[matcher]
        t_precip = precip[matcher]
                
        t_wtd = t_area * t_precip
        
        t_area = ndimage.sum(t_area, t_down, t_d_unq)
        t_wtd = ndimage.sum(t_wtd, t_down, t_d_unq)
        t_precip = t_wtd / t_area
            
        only_nan = np.isnan(precip[np.in1d(unq, t_d_unq)])
        t_d_unq = t_d_unq[only_nan]
        t_area = t_area[only_nan]
        t_precip = t_precip[only_nan]
      
        try:
            np.put(area, np.searchsorted(unq, t_d_unq), t_area)
            np.put(precip, np.searchsorted(unq, t_d_unq), t_precip)
        except:
            print 'Done'      
        
    mod_inputs_x = mod_inputs_x[~mod_inputs_x['PATHID'].isin(unq)]
    mod_inputs_x = mod_inputs_x[['BASINID','PATHID','PRECIP_2YR24HR_MM']]

    tmp_df = pd.DataFrame({'BASINID': np.repeat(np.NaN, len(unq)), 'PATHID': unq, 'PRECIP_2YR24HR_MM': precip})
    
    mod_inputs_x = pd.concat([mod_inputs_x, tmp_df])
    
    mod_inputs_x.to_csv(vars_dir + 'Precip2Yr24hr_mod_' + rpu + '.csv')


print("--- %s seconds ---" % (time.time() - start_time))    




















