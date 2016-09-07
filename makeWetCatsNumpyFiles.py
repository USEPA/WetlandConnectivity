
import arcpy
import os, sys
import pysal as ps
import numpy as np
from collections import deque, defaultdict, OrderedDict

numpy_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats_npy/'
frmto_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/FlowTables/'
watershed_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats/'
    
    #Need to set to where WetCat_function.py is stored
wetcatfunc = 'D:/WorkFolder/WetlandConnectivity/'
sys.path.append(wetcatfunc)  
from WetCat_functions import dbf2DF, children, bastards

files = filter(lambda x: x.endswith(('.dbf')) and not x.count('.tif'), os.listdir(frmto_dir))

for file in files:
    rpu = file[-7:-4]
    print rpu

        #Read in wetland catchments to get list of COMIDs    
    wetcat = watershed_dir + 'WetlandCat_' + rpu + '.tif'
    if not os.path.exists(wetcat + '.vat.dbf'):
        arcpy.BuildRasterAttributeTable_management(wetcat, "Overwrite")
    tbl = dbf2DF(wetcat + '.vat.dbf')
    COMIDs = tbl.VALUE.values      
    
        #Read in from-to table
    flow = dbf2DF(frmto_dir + file)[[1,3]] #Only need columns 1 and 3
    #print flow.head()
    print "Processing region: " + rpu + " with total records = " + str(len(flow))
    flow.columns = ['TOCOMID','FROMCOMID'] #Rename columns
    #----This line may not be needed for watersheds---#
    #----Was part of the process to create path connections---#
    #flow  = flow[flow.FROMCOMID != 0] #Remove paths with FROMCOMID == 0
    fromID = np.array(flow.FROMCOMID) #Make numpy arrays of from and to columns
    toID = np.array(flow.TOCOMID)
    
        #Make dictionary of next up catchment ID
    UpCOMs = defaultdict(list)
    for i in range(0, len(flow), 1):
        FROMID = fromID[i]
        TOID = toID[i]
        UpCOMs[TOID].append(FROMID)                              
        
        #Make and save bastards
    a = map(lambda x: bastards(x, UpCOMs), COMIDs) #Make bastards vector
    lengths = np.array([len(v) for v in a]) #Make lengths vector
    a = np.int32(np.hstack(np.array(a)))    #Convert to 1d vector
    if not os.path.exists(numpy_dir + 'bastards'):
        os.makedirs(numpy_dir + 'bastards')
    np.save(numpy_dir + 'bastards/upCats' + rpu + '.npy', a)
    np.save(numpy_dir + 'bastards/comids' + rpu + '.npy', COMIDs)
    np.save(numpy_dir + 'bastards/lengths' + rpu + '.npy', lengths)
    
         #Make and save children
    a = map(lambda x: children(x, UpCOMs), COMIDs) #Make children vector
    lengths = np.array([len(v) for v in a]) #Make lengths vector
    a = np.int32(np.hstack(np.array(a)))    #Convert to 1d vector
    if not os.path.exists(numpy_dir + 'children'):
        os.makedirs(numpy_dir + 'children')
    np.save(numpy_dir + 'children/upCats' + rpu + '.npy', a)
    np.save(numpy_dir + 'children/comids' + rpu + '.npy', COMIDs)
    np.save(numpy_dir + 'children/lengths' + rpu + '.npy', lengths)   
    
