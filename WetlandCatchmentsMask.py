# -*- coding: utf-8 -*-
"""
Created on Tue Oct 03 12:31:07 2017

@author: mweber
"""

import os, sys, arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")
arcpy.env.workspace = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats"

# Get a list of the rasters in the workspace  
rasters = arcpy.ListRasters()  

# Loop through the list of rasters  
for inRaster in rasters:  
    # Set the outputname for each output to be the same as the input  
    outRaster = outFolder + "\\" + inRaster  