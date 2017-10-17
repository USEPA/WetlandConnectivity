# -*- coding: utf-8 -*-
"""
Created on Tue Oct 03 12:31:07 2017

@author: mweber
"""

import os, sys, arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")
arcpy.env.workspace = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats"
nhddir = 'L:/Priv/CORFiles/Geospatial_Library/Data/RESOURCE/PHYSICAL/HYDROLOGY/NHDPlusV21'
inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
         'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}

inputs_rpu = dict()

for region in inputs.keys():
    for hydro in inputs[region]:
        print 'on region ' + region + ' and hydro number ' + hydro
        for dirs in os.listdir(nhddir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                print dirs
                rpu = dirs[-3:]
                if not inputs_rpu.has_key(rpu):
                    inputs_rpu[rpu] = []
                if not region in inputs_rpu[rpu]:
                    inputs_rpu[rpu].append(region)
                if not hydro in inputs_rpu[rpu]:
                    inputs_rpu[rpu].append(hydro)
                             
# Get a list of the rasters in the workspace  
rasters = arcpy.ListRasters()  

# Loop through the list of rasters  
for raster in rasters: 
    rpu = raster.split('_')[1].split('.')[0]
    fdr = Raster(nhddir + "/NHDPlus" + inputs_rpu[rpu][0] + "/NHDPlus" + inputs_rpu[rpu][1] + "/NHDPlusFdrFac"  + rpu + "/fdr")
    arcpy.env.snapRaster = fdr
    arcpy.env.cellSize = "30"
    arcpy.env.mask = fdr
    arcpy.env.extent = fdr
    temp = Raster(raster)
    temp = Con(IsNull(temp),1)
    temp.save("H:/WorkingData/wetlandjunk/" + raster)
    
# Not run
from os import listdir
import georasters as gr
import numpy as np
indir = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats"

rasters = [f for f in listdir(indir) if f.endswith('.tif')]
i=0

for raster in rasters:
    if i == 0:
        # Get info on raster
        final = gr.from_file(indir + '/' + raster)
#        final.raster.data[final.raster.data > 0] = 1
        final.raster.data[:] = 1
        final.nodata_value = 0
        final.datatype = "Byte"
        final.nodata_value = 255
        final.datatype
        final.raster.
    if i > 0:
        temp = gr.from_file(indir + '/' + raster)
        temp.raster.data[:] = 1
        temp.nodata_value = 0
        temp.datatype = "Byte"
        temp.datatype
        final = gr.merge([final, temp])
    i+=1




final.save("H:/WorkingData/WetCatMask.tif")
