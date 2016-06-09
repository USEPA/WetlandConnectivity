library(raster)
library(rgdal)
library(stringr)

input_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Data'

variables=list.files(input_dir)
streamlist = variables[grep("StreamLink", variables)]
streamlist <-streamlist[grep('\\.tif$',streamlist)]

variables=list.files(input_dir)
wetlandslist = variables[grep("WetlandPoints", variables)]
wetlandslist <-wetlandslist[grep('\\.shp$',wetlandslist)]

count_all=0
count_paths=0
count_nopaths=0
for (i in 1:59){
  streamras = raster(paste0(input_dir,'/',streamlist[i]))
  wetpoint = readOGR(input_dir, strsplit(wetlandslist[i],'\\.')[[1]][1])
  results = extract(streamras, wetpoint)
  wetpoint$STRMLNK_ID =  results
  wetpoint = wetpoint[c(1,6)]
  names(wetpoint)[1] = 'WET_ID'
  wetpoint_with_path = wetpoint[!is.na(wetpoint$STRMLNK_ID),]
  wetpoint_without_path = wetpoint[is.na(wetpoint$STRMLNK_ID),]
  count_all=count_all + nrow(wetpoint)
  count_paths=count_paths + nrow(wetpoint_with_path)
  count_nopaths=count_nopaths + nrow(wetpoint_without_path)
  write.csv(wetpoint, paste0('J:/GitProjects/Wetland Connectivity/LookupTables/AllWetlands_StreamLink_Lookup_',
                             str_sub(strsplit(wetlandslist[i],'\\.')[[1]][1],-3),'.csv'))
  write.csv(wetpoint_with_path, paste0('J:/GitProjects/Wetland Connectivity/LookupTables/WetlandsWithPath_StreamLink_Lookup_',
                             str_sub(strsplit(wetlandslist[i],'\\.')[[1]][1],-3),'.csv'))
  write.csv(wetpoint_without_path, paste0('J:/GitProjects/Wetland Connectivity/LookupTables/WetlandsNoPath_StreamLink_Lookup_',
                             str_sub(strsplit(wetlandslist[i],'\\.')[[1]][1],-3),'.csv'))
  }

