#!/usr/bin/env python

# Script to run zonal statistics for wetland flow paths and wetland basins.
#
# Authors:  Marc Weber<weber.marc@epa.gov>,
#           Ryan Hill<hill.ryan@epa.gov>,
#           Darren Thornbrugh<thornbrugh.darren@epa.gov>,
#           Rick Debbout<debbout.rick@epa.gov>,
#           and Tad Larsen<laresn.tad@epa.gov>
#
# Date: June 8, 2016

import sys
import os
import pandas as pd
import numpy as np
# Load table used in function argument
#ctl = pd.read_csv(sys.argv[1])
ctl = pd.read_csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/ControlTable_WetCat_MW.csv')

# Import system modules
from collections import OrderedDict
from datetime import datetime as dt
import geopandas as gpd
from geopandas.tools import sjoin
sys.path.append(ctl.DirectoryLocations.values[5])  # sys.path.append('D:/Projects/Scipts')
from WetCat_functions import createAccumTable, makeNumpyVectors, makeVPUdict, dbf2DF, GetRasterValueAtPoints
arcpy.CheckOutExtension("spatial")
from arcpy.sa import TabulateArea, ZonalStatisticsAsTable

#####################################################################################################################
# Populate variables from control table
NHD_dir = ctl.DirectoryLocations.values[0]
path_dir = ctl.DirectoryLocations.values[1]
basin_dir = ctl.DirectoryLocations.values[2]
out_dir_paths = ctl.DirectoryLocations.values[3]
out_dir_basins = ctl.DirectoryLocations.values[4]
numpy_dir = '%s/StreamCat_npy' % NHD_dir
lookup_dir = ctl.DirectoryLocations.values[6]

#####################################################################################################################

# Create a list of elevation rasters with paths to use later
elev_rasters = []
inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
          
for region in inputs.keys():
    for hydro in inputs[region]:
        NED_dir = NHD_dir + "/NHDPlus%s/NHDPlus%s"%(region, hydro) + "/NEDSnapshot"
        print NED_dir
        for subdirs in os.listdir(NED_dir):
            elev = "%s/%s/elev_cm" % (NED_dir, subdirs)
            elev_rasters.append(elev)
                
for line in range(len(ctl.values)):  # loop through each FullTableName in control table
    if ctl.run[line] == 1:   # check 'run' field from the table, if 1 run, if not, skip
        # break
        print 'running ' + str(ctl.FullTableName[line])
        accum_type = ctl.accum_type[line]             # Load metric specific variables
        ingrid_dir = ctl.ingrid_dir[line]
#        RPU = int(ctl.by_RPU[line])
#        mask = ctl.use_mask[line]
#        appendMetric = ctl.AppendMetric[line]
#        if appendMetric == 'none':
#            appendMetric = '' 
#        if mask == 0:
#            mask_dir = ''
#        if not os.path.exists(LandscapeLayer) and RPU == 1:  # this is currently a placeholder for scripting the select by location process to get masked point file
#            print "This shouldn't happen yet"
            # make masked tables for points, Used QGIS 'point sampling tool' to make the rpBuf100 files
        FullTableName = ctl.FullTableName[line]
        summaryfield = None
        if type(ctl.summaryfield[line]) == str:
            summaryfield = ctl.summaryfield[line].split(';')
        if accum_type == 'Point':  # Load in point geopandas table and Pct_Full table 
            if mask == 0:
                pct_full_file = ctl.DirectoryLocations.values[4]
            if mask == 1:
                pct_full_file = ctl.DirectoryLocations.values[8]
            pct_full = pd.read_csv(pct_full_file)
            points = gpd.GeoDataFrame.from_file(LandscapeLayer)
#        Connector = "%s/%s_connectors.csv" % (out_dir, FullTableName)  # File string to store InterVPUs needed for adjustments
        catTime = dt.now()
        files = filter(lambda x: x.endswith(('.tif')) and x.count(('Stream')) and not x.count('FDR'), os.listdir(path_dir))
        for zone in files:
            inZoneData = path_dir + '/' + zone
            LandscapeLayer = ctl.LandscapeLayer[line]
            if not os.path.exists(out_dir_paths + '/' + FullTableName + '_' + zone.split('.')[0][-3:] + '.csv'):
                if LandscapeLayer.count('.tif') or LandscapeLayer.count('.img'):
                    outTable ="%s/zonalstats_%s_%s.dbf" % (out_dir_paths,LandscapeLayer.split("/")[-1].split(".")[0], zone.split('.')[0][-3:])
                else:
                    outTable ="%s/zonalstats_%s%s.dbf" % (out_dir_paths,LandscapeLayer.split("/")[-1], zone.split('.')[0][-3:])
            if ctl.FullTableName[line]=='Elev':
                LandscapeLayer  = [x for x in elev_rasters if x.count(zone.split('.')[0][-3:])]
                LandscapeLayer = LandscapeLayer[0]
                arcpy.env.cellSize = "30"
                arcpy.env.snapRaster = LandscapeLayer
                if accum_type == 'Continuous':
                    if not arcpy.Exists(outTable):
                        ZonalStatisticsAsTable(inZoneData, 'VALUE', LandscapeLayer, outTable, "DATA", "ALL")
            else:
                LandscapeLayer = '%s/%s' % (ingrid_dir, ctl.LandscapeLayer[line]) 
                arcpy.env.cellSize = "30"
                arcpy.env.snapRaster = inZoneData
                if accum_type == 'Categorical':
                    if not arcpy.Exists(outTable):
                        TabulateArea(inZoneData, 'VALUE', LandscapeLayer, "Value", outTable, "30")
                if accum_type == 'Continuous':
                    if not arcpy.Exists(outTable):
                        ZonalStatisticsAsTable(inZoneData, 'VALUE', LandscapeLayer, outTable, "DATA", "ALL")
  
            
            in2accum = len(cat.columns)
        print 'Cat Results Complete in : ' + str(dt.now()-catTime)     
        try:
            in2accum
        except NameError:
            in2accum = len(pd.read_csv('%s/%s_%s.csv' % (out_dir, FullTableName, zone)).columns)
        accumTime = dt.now()
        for zone in inputs:
            cat = pd.read_csv(out_dir + '/' + FullTableName + '_' + zone + '.csv')
            in2accum = len(cat.columns)
            if len(cat.columns) == in2accum:
                up = createAccumTable(cat, numpy_dir, zone, tbl_type='UpCat')
                ws = createAccumTable(cat, numpy_dir, zone, tbl_type='Ws')
                if zone in interVPUtbl.ToZone.values:
                    cat = pd.read_csv(out_dir + '/' + FullTableName + '_' + zone + '.csv')
                if zone in interVPUtbl.FromZone.values:
                    interVPU(ws, cat.columns[1:], accum_type, zone, Connector, interVPUtbl.copy(), summaryfield)
                upFinal = pd.merge(up, ws, on='COMID')
                final = pd.merge(cat, upFinal, on='COMID')
                final.to_csv(out_dir + '/' + FullTableName + '_' + zone + '.csv', index=False)
        print 'Accumulation Results Complete in : ' + str(dt.now()-accumTime)
print "total elapsed time " + str(dt.now()-totTime)

# Create lookup table for wetland flow paths and wetlands (there are more flow paths than wetlands, and numbers are different)
# Also, create lookup table to match each wetland to an NHDPlus catchment
# We generate these lookups using the wetland pour point for each NHDPlus raster processing unit
WetPointsList =  filter(lambda x: x.endswith(('.shp')) and x.count(('Points')) and not x.count('xml'), os.listdir(path_dir))
StreamLinkList = filter(lambda x: x.endswith(('.tif')) and x.count(('Stream')) and not x.count('FDR'), os.listdir(path_dir))
count_all=0
count_paths=0
count_nopaths=0
for points in WetPointsList: 
    print 'working on ' + points
    Inpoints = path_dir + '/' + points
    InStreamRas = path_dir + '/' + next(x for x in StreamLinkList if x.count(Inpoints.split('.')[0][-3:]))
    results = GetRasterValueAtPoints(InStreamRas, Inpoints, "GRID_CODE")
    results.columns = ['WET_ID','STRMLNK_ID']
    # get rid of rows in tables for wetlands where there is no flow path (i.e. adjacent to stream)
    has_path = results['STRMLNK_ID'] > 0
    no_path = results['STRMLNK_ID'] < 0
    results_with_path = results[has_path]
    results_without_path = results[no_path]
    print 'writing results'
    results.to_csv(lookup_dir + '/AllWetlands_StreamLink_Lookup_' + Inpoints.split('.')[0][-3:] + '.csv', index=False)
    results_with_path.to_csv(lookup_dir + '/WetlandsWithPath_StreamLink_Lookup_' + Inpoints.split('.')[0][-3:] + '.csv', index=False)
    results_without_path.to_csv(lookup_dir + '/WetlandsNoPath_StreamLink_Lookup_' + Inpoints.split('.')[0][-3:] + '.csv', index=False)
    count_all+=results.shape[0]
    count_paths+=results_with_path.shape[0]
    count_nopaths+=results_without_path.shape[0]

# And create lookup tables for wetlands and corresponding NHDPlus catchments    
#inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
#          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}

inputs = {'MS':['08']}   
for region in inputs.keys():
    for hydro in inputs[region]:
        print 'working on ' + hydro
        InCats = NHD_dir + "/NHDPlus%s/NHDPlus%s"%(region, hydro) + "/NHDPlusCatchment/Catchment.shp"
        CatFeat = gpd.GeoDataFrame.from_file(InCats)
        files = filter(lambda x: x.count('FdrNull') and not x.count('.txt'), os.listdir(NHD_dir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)))
        RPUs = [x[-3:] for x in files]
        WetPointsInRgn = [x for x in WetPointsList if x.split('.')[0][-3:] in RPUs]

        for wetlands in WetPointsInRgn:
            if not os.path.isfile(lookup_dir + '/Wetlands_NHDPlusCat_Lookup_' + wetlands.split('.')[0][-3:] + '.csv'):
                print 'working on ' + wetlands
                WetFeat = gpd.GeoDataFrame.from_file(path_dir + '/' + wetlands)
                CatFeat = CatFeat.to_crs(WetFeat.crs)
                WetlandsCats = sjoin(WetFeat, CatFeat, how="inner", op='intersects')
                WetlandsCats = WetlandsCats[['GRID_CODE','FEATUREID']]
                WetlandsCats.columns = ['WET_ID','COMID']
                WetlandsCats.to_csv(lookup_dir + '/Wetlands_NHDPlusCat_Lookup_' + wetlands.split('.')[0][-3:] + '.csv', index=False)
    


