# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 14:30:29 2017

@author: RHill04
"""
import glob, os
import numpy as np
import pandas as pd
from scipy import ndimage

year = '2011'
numpy_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/WetlandPath/WetPaths_npy/updown_framework/'
nload_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Incremental_N_Inputs/'
#rpu = '09a'

files = os.listdir(numpy_dir)
files = filter(lambda k: 'unq' in k, files)

#Loss factor to be defined along path and multiplied by travel time
loss_factor = 0

for i in files:
    print i
    suffix =  i[len('unq_'):]
    rpu = suffix[:len('.npy')-1]
        #Load numpy arrays
    unq = np.load(numpy_dir + i) 
    down = np.load(numpy_dir + 'down_' + suffix) 
    seq = np.load(numpy_dir + 'seq_' + suffix) 
        #Create empty arrays with same len as unq
    freq = np.repeat(np.NAN, len(unq))
    tt = np.repeat(np.NAN, len(unq))
    ncat = np.repeat(np.NAN, len(unq))
    load = np.repeat(0., len(unq))
    w_nout = np.repeat(0., len(unq))
    pflag = np.repeat(np.NAN, len(unq))
        #Read in table (define bunk columsn to dev code)
    inputs_x = pd.read_csv(nload_dir + 'FinalIncrementalTable_' + rpu + '.csv')
    inputs_x['ncat'] = inputs_x[['Nfert','Nmanure','Ncbnf','Ncmaq']].sum(axis=1)
    inputs_x['path_flag'] = 1
    inputs_x.path_flag.loc[inputs_x.WET_ID.isnull()] = 0
        #Pull out pathids and other columns
    pathid = np.array(inputs_x.PATHID)
    matcher0 = np.in1d(pathid, unq) #Order ids with unq vector
    pathid = pathid[matcher0] #place all inputs in this order
    p_freq = np.array(inputs_x.Freq)[matcher0]
    p_tt = np.array(inputs_x.t_final)[matcher0]
    p_ncat = np.array(inputs_x.ncat)[matcher0]
    p_pflag = np.array(inputs_x.path_flag)[matcher0]
        #Fill in empty arrays in correct locations with values  
    order = np.searchsorted(unq, pathid)
    freq[order] = p_freq
    tt[order] = p_tt
    pflag[order] = p_pflag
    ncat[order] = p_ncat  
        
    for k in np.unique(seq):
        print k
        matcher = np.in1d(seq, k)
        t_unq = unq[matcher]
        t_down = down[matcher]
        t_d_unq = np.unique(t_down)  
        t_freq = freq[matcher]
        t_pflag = pflag[matcher]
        t_tt = tt[matcher]  
        t_ncat = np.nan_to_num(ncat[matcher])
        t_load = load[matcher]
        t_load = t_load + t_ncat 
                     
        t_nout = t_freq * ((t_load - np.power(10, (0.943 * np.log10(t_load) - 0.033)) * t_pflag) - (loss_factor * t_tt))    
        
        t_nout = np.nan_to_num(t_nout)
        np.put(w_nout, np.searchsorted(unq, t_unq), t_nout)
        
        t_nout = ndimage.sum(t_nout, t_down, t_d_unq)
        
        try:
            np.put(load, np.searchsorted(unq, t_d_unq), t_nout)
        except:
            print 'Done'

#ID = 476923
#
#ncat[np.in1d(unq,ID)]
#load[np.in1d(unq,ID)]
#freq[np.in1d(unq,ID)]
#tt[np.in1d(unq,ID)]
#pflag[np.in1d(unq,ID)]
#w_nout[np.in1d(unq,ID)]
#
#pathid[np.in1d(pathid, ID)]
#WET_ID[np.in1d(pathid, ID)]
#
#
#test_load = load[np.in1d(unq,ID)] + ncat[np.in1d(unq,ID)]
#freq[np.in1d(unq,ID)] * (test_load - np.power(10, (0.943 * np.log10(test_load) - 0.033)))
