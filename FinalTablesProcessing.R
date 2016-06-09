library(stringr)
path_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Accumulation'

variables=list.files(path_dir)
elevmaxlist = variables[grep("elev_cm_max", variables)]
elevminlist = variables[grep("elev_cm_min", variables)]
i=0
for (i in 1:59){
  elevmax = read.csv(paste0(path_dir,'/',elevmaxlist[i]))
  elevmax$MAX = elevmax$MAX * .01
  elevmin = read.csv(paste0(path_dir,'/',elevminlist[i]))
  elevmax$MAX = elevmax$MAX * .01
  elevmax$MIN = elevmin$MIN[match(elevmax$COMID, elevmin$COMID)]
  elevmax$RISE = elevmax$MAX - elevmax$MIN
  elevmax[c(1,4)]
  write.csv(elevmax, paste0(path_dir, '/Shallow', str_sub(strsplit(elevmaxlist[i],'\\.')[[1]][1],-3),'.csv'))
  }

library(matrixStats)
nlcdlist = variables[grep("nlcd2011", variables)]
mannings = read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/LookupTables/NLCD_Mannings_Lookup.csv')
head(mannings)
for (i in 1:59){
  nlcd = read.csv(paste0(path_dir,'/',nlcdlist[i]))
  head(nlcd)
  nlcd$Total <- rowSums(nlcd[,2:16])
  
  #calculate %s for each nlcd category
  for (k in 2:16){
    nlcd[,k] = 100.0 * nlcd[,k]/nlcd[,17]
  } 
  nlcd = nlcd[c(1:16)]
  #calculate mannings for each category
  for (m in 2:16){
    nlcd[,m] = (mannings$Mannings[match(names(nlcd)[m], mannings$NLCD)])^(nlcd[,m])
  } 
  #calculate final mannings geometric mean
  nlcd$GeoMean = (rowProds(as.matrix(nlcd[,2:16])))^(1/100)
  names(nlcd)[1] = 'WETID'
  write.csv(nlcd, paste0(path_dir, '/Mannings', str_sub(strsplit(nlcdlist[i],'\\.')[[1]][1],-3),'.csv'))
}

