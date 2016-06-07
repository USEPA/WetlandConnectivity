#!/usr/bin/env python

# Script to call StreamCat functions script and run allocation and
# accumulation of landscape metrics to NHDPlus catchments.  Assumes
# landscape rasters in desired projection with appropriate
# pre-processing to deal with any reclassing of values or recoding
# of NA, and directories of NHDPlusV2 data installed in standard
# directory format.
#          __                                       __
#    _____/ /_________  ____  ____ ___  _________ _/ /_ 
#   / ___/ __/ ___/ _ \/ __ `/ __ `__ \/ ___/ __ `/ __/
#  (__  ) /_/ /  /  __/ /_/ / / / / / / /__/ /_/ / /_ 
# /____/\__/_/   \___/\__,_/_/ /_/ /_/\___/\__,_/\__/ 
#
# Authors:  Marc Weber<weber.marc@epa.gov>,
#           Ryan Hill<hill.ryan@epa.gov>,
#           Darren Thornbrugh<thornbrugh.darren@epa.gov>,
#           Rick Debbout<debbout.rick@epa.gov>,
#           and Tad Larsen<laresn.tad@epa.gov>
#
# Date: November 29, 2015
#
# NOTE: run script from command line passing directory and name of this script
# and then directory and name of the control table to use like:
# > Python "F:\Watershed Integrity Spatial Prediction\Scripts\StreamCat.py"
# L:\Priv\CORFiles\Geospatial_Library\Data\Project\SSWR1.1B\ControlTables\ControlTable_StreamCat.csv
# --------------------------------------------------------

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
sys.path.append(ctl.DirectoryLocations.values[5])  # sys.path.append('D:/Projects/Scipts')
from WetCat_functions import createAccumTable, makeNumpyVectors, makeVPUdict, dbf2DF
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
                    ZonalStatisticsAsTable(inZoneData, 'VALUE', LandscapeLayer, outTable, "DATA", "ALL")
            else:
                LandscapeLayer = '%s/%s' % (ingrid_dir, ctl.LandscapeLayer[line]) 
                arcpy.env.cellSize = "30"
                arcpy.env.snapRaster = inZoneData
                if accum_type == 'Categorical':
                    TabulateArea(inZoneData, 'VALUE', LandscapeLayer, "Value", outTable, "30")
                if accum_type == 'Continuous':
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

