# -*- coding: utf-8 -*-
"""
Created on Tue May 09 15:41:35 2017

@author: mweber
"""

import arcpy
import os
from arcpy.sa import *
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

Wetlands_2001 = Raster('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2001/AllWetlands_rpu/Wetlands_17c.tif')
Wetlands_2011 = Raster('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/AllWetlands_rpu/Wetlands_17c.tif')

Wetlands_2001 = Con(IsNull(Wetlands_2001), 0, Wetlands_2001)
Wetlands_2011 = Con(IsNull(Wetlands_2011), 0, Wetlands_2011)

# Execute Combine
outCombine = Combine([Wetlands_2001,Wetlands_2011])
outCombine.save("H:/WorkingData/Wetlands17c_Combine.tif")

# Clip to just Willamette Basin for now
Willamette = "H:/WorkingData/WillametteBasin.shp"

arcpy.Clip_management(in_raster="H:/WorkingData/Wetlands17c_Combine.tif", rectangle="-2207615.89186445 2535810.35042075 -1957039.79228252 2847310.7592463", out_raster="H:/WorkingData/WillametteWetlandsCombine.tif",
                      in_template_dataset=Willamette, nodata_value="-2147483647", clipping_geometry="ClippingGeometry", 
                      maintain_clipping_extent="NO_MAINTAIN_EXTENT")