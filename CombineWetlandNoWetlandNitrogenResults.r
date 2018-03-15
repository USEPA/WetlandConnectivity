pointn <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetDrainPointN.csv')
head(pointn)
summary(pointn$WsPointN)



full <- pointn[c(1,2,5)]
names(full)[3] <- 'PointN_KgN'
full$PointN_KgN[is.na(full$PointN_KgN)] <- 0

wetcmaq <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetDrainCMAQ.csv')
full$WetAtmN_KgN <- wetcmaq$WsCMAQLoad[match(full$SITE_ID, wetcmaq$SITE_ID)]
full$WsDrainAreaSqKm <- wetcmaq$WsDrainAreaSqKm[match(full$SITE_ID, wetcmaq$SITE_ID)]

nowetcmaq <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/NoWetDrainCMAQ.csv')
nowetcmaq$NoWetAtmN_KgN <- nowetcmaq$WsAreaSqKm * 100 * nowetcmaq$TD_NWs
full$NonWetAtmN_KgN <- nowetcmaq$NoWetAtmN_KgN[match(full$SITE_ID, nowetcmaq$SITE_ID)]
full$NonWetDrainAreaSqKm <- nowetcmaq$WsAreaSqKm[match(full$SITE_ID, nowetcmaq$SITE_ID)]

wetfert <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetDrainFert.csv')
full$WetFert_KgN <- wetfert$WsFertLoad[match(full$SITE_ID, wetfert$SITE_ID)]

nowetfert <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/NoWetDrainFert.csv')
nowetfert$NoWetFert_KgN <- nowetfert$WsAreaSqKm * 100 * nowetfert$FertWs
full$NoWetFert_KgN <- nowetfert$NoWetFert_KgN[match(full$SITE_ID, nowetfert$SITE_ID)]

wetcbnf <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetDrainCbnf.csv')
full$WetCbnf_KgN <- wetcbnf$WsCbnfLoad[match(full$SITE_ID, wetcbnf$SITE_ID)]

nowetcbnf <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/NoWetDrainCBNF.csv')
nowetcbnf$NoWetCbnf_KgN <- nowetcbnf$WsAreaSqKm * 100 * nowetcbnf$CBNFWs
full$NoWetCbnf_KgN <- nowetcbnf$NoWetCbnf_KgN[match(full$SITE_ID, nowetcbnf$SITE_ID)]

wetmanure <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetDrainManure.csv')
full$WetManure_KgN <- wetmanure$WsManureLoad[match(full$SITE_ID, wetmanure$SITE_ID)]

nowetmanure <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/NoWetDrainManure.csv')
nowetmanure$NoWetManure_KgN <- nowetmanure$WsAreaSqKm * 100 * nowetmanure$ManureWs
full$NoWetManure_KgN <- nowetmanure$NoWetManure_KgN[match(full$SITE_ID, nowetmanure$SITE_ID)]
names(full)[6] <- 'WetWsDrainAreaSqKm'
full$FullWsAreaSqKm <- full$WetWsDrainAreaSqKm + full$NonWetDrainAreaSqKm 
full <- full[c(1:3,6:7,14,4:5,8:13)]

wetdist <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetlandDist.csv')
names(wetdist)[12:14] <- c('High','Low','None')
wetdist$DomWetDist <- colnames(wetdist[,12:14])[max.col(wetdist[,12:14], ties.method="first")]
wetdist$DomWetDist[wetdist$WsWetAreaSqKm==0] <- 'None'
full$DomWetDist <- wetdist$DomWetDist[match(full$SITE_ID, wetdist$SITE_ID)]

wetmag <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetlandMag.csv')
names(wetmag)[16:20] <- c('VerySlow','Slow','Moderate','Fast','VeryFast')
wetmag$DomWetMag <- colnames(wetmag[,16:20])[max.col(wetmag[,16:20], ties.method="first")]
wetmag$DomWetMag[wetmag$WsWetAreaSqKm==0] <- 'NA'
full$DomWetMag <- wetmag$DomWetMag[match(full$SITE_ID, wetmag$SITE_ID)]

wetfreq <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetlandFreq.csv')
names(wetfreq)[14:16] <- c('High','Low','Med')
wetfreq$DomWetFreq <- colnames(wetfreq[,14:16])[max.col(wetfreq[,14:16], ties.method="first")]
wetfreq$DomWetFreq[wetfreq$WsWetAreaSqKm==0] <- 'NA'
full$DomWetFreq <- wetfreq$DomWetFreq[match(full$SITE_ID, wetfreq$SITE_ID)]

wettype <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetlandType.csv')
names(wettype)[16:19] <- c('Overland','Riparian','Shallow','ShallowDeep')
wettype$DomWetType <- colnames(wettype[,16:19])[max.col(wettype[,16:19], ties.method="first")]
wettype$DomWetType[wettype$WsWetAreaSqKm==0] <- 'NA'
full$DomWetType <- wettype$DomWetType[match(full$SITE_ID, wettype$SITE_ID)]

wetmagavg <- read.csv('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/WetlandMagAvg.csv')
full$AvgWetMag <- wetmagavg$WsAvgConMag[match(full$SITE_ID, wetmagavg$SITE_ID)]
full <- full[c(1:16,19,17:18)]
# Add NRSA Area for comparison purposes
library(readxl)
nrsa_orig <- read_excel('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/Bellmore_Tables/N data for publication.xlsx')
full$NRSA_AreaSqKm <- nrsa_orig$area_km2[match(full$SITE_ID,nrsa_orig$SITE_ID)]
plot(full$FullWsAreaSqKm, full$NRSA_AreaSqKm)
write.csv(full, 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/NitrogenModeling/NRSA_Results/NRSA_NitrogenResults.csv', 
          row.names = FALSE)

