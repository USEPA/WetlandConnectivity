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
nload_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Incremental_N_Inputs/'
vars_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Incremental_N_Inputs/'

files = os.listdir(numpy_dir)
files = filter(lambda k: 'unq' in k, files)

#Loss factor to be defined along path and multiplied by travel time
loss_factor = 0
start_time = time.time()
for i in files:
    start_time2 = time.time()
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
    wetid = np.repeat(np.NAN, len(unq))
    wetarea = np.repeat(np.NAN, len(unq))
        #Read in table (define bunk columsn to dev code)
    inputs = pd.read_csv(nload_dir + 'FinalIncrementalTable_' + rpu + '.csv')
        #Multiply by catchment area (convert to hectares) and convert Kg to g
    inputs['ncat'] = inputs[['Nfert','Nmanure','Ncbnf','Ncmaq']].sum(axis=1) 
    inputs['ncat'] = inputs.ncat * (inputs.WetCatAreaSqKm * 100) * 1000 
    inputs['path_flag'] = 1
    inputs.loc[inputs.WET_ID.isnull(), 'path_flag'] = 0
        #Pull out pathids and other columns
    pathid = np.array(inputs.PATHID)
    matcher0 = np.in1d(pathid, unq) #Order ids with unq vector
    pathid = pathid[matcher0] #place all inputs in this order
        #Fill in empty arrays in correct locations with values  
    order = np.searchsorted(unq, pathid)
    freq[order] = np.array(inputs.Freq)[matcher0]
    tt[order] = np.array(inputs.t_final)[matcher0]
    pflag[order] = np.array(inputs.path_flag)[matcher0]
    ncat[order] = np.array(inputs.ncat)[matcher0]  
    wetid[order] = np.array(inputs.WET_ID)[matcher0]
    wetarea[order] = np.array(inputs.WetAreaSqKm)[matcher0] * 1e6
        
    for k in np.unique(seq):
        #print k
        matcher = np.in1d(seq, k)
        #print np.sum(matcher)
        t_unq = unq[matcher]
        t_down = down[matcher]
        t_d_unq = np.unique(t_down)  
        t_freq = freq[matcher]
        t_pflag = pflag[matcher]
        t_tt = tt[matcher]  
        t_ncat = np.nan_to_num(ncat[matcher])
        t_wa = wetarea[matcher]
        t_load = load[matcher]
        t_load = t_load + t_ncat 
        bool_pflag = t_pflag == 1
        
        t_nout = np.repeat(0., len(t_load)) 
        t_nout[bool_pflag] = 0.99 * np.log10(t_load[bool_pflag]/t_wa[bool_pflag]) - 0.46
        t_nout[bool_pflag] = np.power(10, t_nout[bool_pflag]) * t_wa[bool_pflag]
        t_nout = t_load - t_nout
        t_nout[bool_pflag] = t_nout[bool_pflag] * t_freq[bool_pflag]
        t_nout = t_nout - (loss_factor * t_tt)
        t_nout = np.nan_to_num(t_nout)        
        if k == 1:
            effic = (t_load[bool_pflag]-t_nout[bool_pflag])/t_load[bool_pflag]
            effic_id = t_unq[bool_pflag]
        else: 
            effic = np.append(effic, (t_load[bool_pflag]-t_nout[bool_pflag])/t_load[bool_pflag])
            effic_id = np.append(effic_id, t_unq[bool_pflag])
            
        np.put(w_nout, np.searchsorted(unq, t_unq), t_nout)
        
        t_nout = ndimage.sum(t_nout, t_down, t_d_unq)
        
        try:
            np.put(load, np.searchsorted(unq, t_d_unq), t_nout)
        except:
            print 'Done'
            
    #Run process for single wetlands with direct link to streams
    inputs = inputs[~inputs['PATHID'].isin(unq)]
    ncat = np.array(inputs.ncat)
    nload = ncat
    wetarea = np.array(inputs.WetAreaSqKm) * 1e6
    pid = np.array(inputs.PATHID)
    pflag = np.array(inputs.path_flag)
    tt = np.array(inputs.t_final)
    freq = np.array(inputs.Freq)
    wid = np.array(inputs.WET_ID)
    sq = np.repeat(np.nanmax(seq), len(ncat))

    tmpn = 0.99 * np.log10(ncat/wetarea) - 0.46
    tmpn = np.power(10, tmpn) * wetarea
    ncat = (ncat - tmpn) * freq
    ncat = ncat - (loss_factor * tt)
    effic = np.append(effic, (nload - ncat)/nload)
    effic_id = np.append(effic_id, pid)
    ncat[ncat < 0] = 0 #In case any end up negative
    ncat = np.append(ncat, w_nout)
    ncat = np.nan_to_num(ncat)
    ncat = ncat / 1000.
    
    wid = np.append(wid, wetid)
    pid = np.append(pid, unq)
    sq = np.append(sq, seq)
    
    out_df = pd.DataFrame({'WET_ID': wid, 'PATHID': pid, 'Sequence': sq, 'N_out_kg': ncat})
    out_df2 = pd.DataFrame({'PATHID': effic_id, 'Efficiency': effic} )
    
    out_df.to_csv(vars_dir + 'N_WetlandOutput_' + rpu + '.csv', index=False)
    out_df2.to_csv(vars_dir + 'WetlandEfficiency_' + rpu + '.csv', index=False)
    print("--- %s seconds ---" % (time.time() - start_time2)) 

print("--- TOTAL TIME: %s seconds ---" % (time.time() - start_time)) 


ID = 415

#
#t_unq[np.in1d(t_unq, ID)]
#t_down[np.in1d(t_unq, ID)]
#t_freq[np.in1d(t_unq, ID)]
#t_pflag[np.in1d(t_unq, ID)]
#t_ncat[np.in1d(t_unq, ID)]
#t_load[np.in1d(t_unq, ID)]
#t_wa[np.in1d(t_unq, ID)]
#
#w_nout[np.in1d(unq, ID)]
#

pid[np.in1d(pid, ID)]
ncat[np.in1d(pid, ID)]

#
#
#t_nout[np.in1d(t_unq, ID)]
#
#
seq[np.in1d(unq, ID)]
load[np.in1d(unq, ID)]
ncat[np.in1d(unq, ID)]
w_nout[np.in1d(unq, ID)]

