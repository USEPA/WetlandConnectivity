import pandas as pd
import numpy as np
import os, sys

wetcatfunc = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/ScriptsArchive/'
sys.path.append(wetcatfunc)  
from WetCat_functions import dbf2DF, Accumulation

#ctl_path = 'J:/GitProjects/Wetland Connectivity/WetlandScripts/'
ctl_path = 'C:/Users/mweber/Git Projects/WetlandConnectivity/WetlandScripts/'
ctl = pd.read_csv(ctl_path + 'ControlTable_Wetlands_NLCD2011.csv')

    #Use any of the numpy files to get list of regions
numpy_dir = ctl.DirectoryLocations.values[8] + '/'
files = filter(lambda x: x.endswith(('.npy')) and x.count('lengths'), os.listdir(numpy_dir+'children'))

for line in range(len(ctl.values)):
    if ctl.run[line] == 1:   
        
        zonal_type = str.upper(ctl.MetricType[line]) #Type of zonal and accumulation metric to process
        var = ctl.Final_Table_Name[line] #Name of variable to be processed
        tbl_type = ctl.path_basin[line] #Name of type of table (basin or path)
        ID_column = str.capitalize(tbl_type) + 'ID'
        accum_type = ctl.accum_type[line]
            # Populate variables from control table
        if tbl_type == 'path':
            zonal_dir = ctl.DirectoryLocations.values[3] + '/'
            numpy_dir = ctl.DirectoryLocations.values[8] + '/'
            path_dir = ctl.DirectoryLocations.values[1] + '/'
            out_accum = ctl.DirectoryLocations.values[9] + '/'
            npIDvect = 'PathIDs'
            npNetwork = 'downPaths'
        else:
            zonal_dir = ctl.DirectoryLocations.values[4] + '/'    
            numpy_dir = ctl.DirectoryLocations.values[7] + '/'    
            path_dir = ctl.DirectoryLocations.values[2] + '/'
            out_accum = ctl.DirectoryLocations.values[10] + '/'     
            npIDvect = 'comids'
            npNetwork = 'upCats'
            
        print '---- Running: ' + var + ' ' + zonal_type + ' ----'
        for file in files:
            region = file[7:10]
            print region  
            startTime = time.time() 
            outFile = out_accum + var + '_' + zonal_type + '_' + region + '.csv'
            zonal_file =  zonal_dir + var + '_' + region + '.dbf'
                #Read in zonal table
            arr = dbf2DF(zonal_file)  
                #Which columns to keep or drop for accumulation
            if zonal_type == 'MEAN':    
                arr = arr[['VALUE', 'SUM', 'COUNT']]
            elif zonal_type != 'MEAN' and zonal_type != 'PERCENT':
                arr = arr[['VALUE', zonal_type]]                
                #Read in numpy vectors                        
            IDs = np.load(numpy_dir + 'children/' + npIDvect + region + '.npy')
            lengths = np.load(numpy_dir + 'children/lengths' + region + '.npy')
            network = np.load(numpy_dir + 'children/' + npNetwork + region + '.npy')
                #Make sure all path or ws IDs are accounted for
            if len(arr) != len(IDs):
                if tbl_type == 'path':
                    allIDs = dbf2DF(path_dir + 'StreamLink' + region + '.tif.vat.dbf')[['VALUE']]
                else:
                    allIDs = dbf2DF(path_dir + 'WetlandCat_' + region + '.tif.vat.dbf')[['VALUE']]
                arr = pd.merge(arr, allIDs, on = 'VALUE', how = 'right')

            df = Accumulation(arr, IDs, lengths, network, tbl_type=tbl_type, ID_column=ID_column, zonal_type=zonal_type)
            df.to_csv(out_accum + var + '_' + zonal_type + '_' + region + '.csv', index=False)
            print "Minutes for this region: " + str((time.time()-startTime) / 60.0)





























