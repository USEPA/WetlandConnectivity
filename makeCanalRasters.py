# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 10:27:18 2016

@author: mweber
"""

import geopandas as gpd
import rasterio
import fiona
from rasterio import features
import os
from datetime import datetime as dt

def rasterize(convert_to_rast, out_rast, meta, field):
    with rasterio.open(out_rast, 'w', **meta) as out:
        out_arr = out.read(1)
        # this is where we create a generator of geom, value pairs to use in rasterizing
        shapes = ((geom,value) for geom, value in zip(convert_to_rast.geometry, convert_to_rast[field]))
        
        burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
        out.write_band(1, burned)       
                
if __name__ == '__main__':
    NHDDir = "H:/NHDPlusV21"
    inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
    for region in inputs.keys():
        for hydro in inputs[region]:
            print 'on region ' + region + ' and hydro number ' + hydro
            start = dt.now()
            rst = rasterio.open(NHDDir + '/NHDPlus' + region + '/NHDPlus' + hydro + '/NHDPlusCatchment/cat')
            convert_to_rast = gpd.read_file(NHDDir + '/NHDPlus' + region + '/NHDPlus' + hydro + '/NHDSnapshot/Hydrography/NHDFlowline.shp') 
            convert_to_rast = convert_to_rast.loc[convert_to_rast['FTYPE'] == 'CanalDitch']
            convert_to_rast['Junk'] = 1    
            if rst.crs != convert_to_rast.crs:
                convert_to_rast = convert_to_rast.to_crs(rst.crs)
            meta = rst.meta.copy()
            meta.update(compress='lzw', dtype='uint8', nodata=0, driver='GTiff')    
            out_rast = 'H:/WorkingData/Canals_' + hydro + '.tif'
            rasterize(convert_to_rast, out_rast, meta, 'Junk')
            print dt.now() - start
            
