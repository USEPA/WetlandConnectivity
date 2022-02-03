library(dplyr)

year = '2011'
rds_path <- 'D:/WorkFolder/WetlandConnectivity/WetConnect_Oct2019/Wetlands_NLCD2011/FinalTables/'
rpus <- read.csv('L:/Priv/CORFiles/Geospatial_Library_Projects/StreamCat/COMID_HydroRegion_RPU.csv')


fullwetlands <- readRDS(paste0(rds_path, 'WetConnectMetrics_',year,'--preliminary.rds'))

tmp1 <- fullwetlands %>% group_by(COMID) %>% summarise(wetarea = sum(WetAreaSqKm))

tmp2 <- fullwetlands[fullwetlands$Type == "NRSur",]
tmp2 <- tmp2 %>% group_by(COMID) %>% summarise(NRSur = sum(WetAreaSqKm))

tmp3 <- fullwetlands[fullwetlands$Type == "Ripar",]
tmp3 <- tmp3 %>% group_by(COMID) %>% summarise(Ripar = sum(WetAreaSqKm))

tmp4<- fullwetlands[fullwetlands$Type == "NRSubPd",]
tmp4 <- tmp4 %>% group_by(COMID) %>% summarise(NRSubPd = sum(WetAreaSqKm))

tmp5<- fullwetlands[fullwetlands$Type == "NRSubWd",]
tmp5 <- tmp5 %>% group_by(COMID) %>% summarise(NRSubWd = sum(WetAreaSqKm))

wd <- 'L:/Priv/CORFiles/Geospatial_Library_Projects/StreamCat/FTP_Staging/StreamCat/HydroRegions/'
files <- list.files(wd, 'BFI_')

for(i in 1:length(files)){
  print(i)
  tmp <- read.csv(paste0(wd, files[i]))
  if(i == 1){
    outdf <- tmp
  }else{
    outdf <- rbind(outdf, tmp)
  }
}

outdf <- subset(outdf, select=c(COMID, CatAreaSqKm))

outdf <- merge(outdf, tmp1, by='COMID', all.x=T)
outdf <- merge(outdf, tmp2, by='COMID', all.x=T)
outdf <- merge(outdf, tmp3, by='COMID', all.x=T)
outdf <- merge(outdf, tmp4, by='COMID', all.x=T)
outdf <- merge(outdf, tmp5, by='COMID', all.x=T)

outdf$NRSur <- (outdf$NRSur / outdf$wetarea) * 1000
outdf$Ripar <- (outdf$Ripar / outdf$wetarea) * 1000
outdf$NRSubPd <- (outdf$NRSubPd / outdf$wetarea) * 1000
outdf$NRSubWd <- (outdf$NRSubWd / outdf$wetarea) * 1000
outdf$pctwet <- (outdf$wetarea / outdf$CatAreaSqKm) * 1000

outdf[is.na(outdf)] <- 0

type_names = names(outdf)[4:7]

outdf$Dom <- type_names[apply(outdf[,4:7], 1, which.max)]
outdf$Dom <- ifelse(outdf$wetarea == 0, NA, outdf$Dom)

outdf$DomCode <- apply(outdf[,4:7], 1, which.max)
outdf$DomCode <- ifelse(outdf$wetarea == 0, NA, outdf$DomCode)


write.csv(outdf, 'D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/maps-20200124/type_permil_newclasses_20200128.csv', row.names = F)


#------------------------------
#Plots

tmp <- fullwetlands[, c('Type','MagOv','MagSh','ImpDrImperv','ImpDrAg','ImpPaLev', 'ImpPaCan','FreqClsPa','WetAreaSqKm','ImpPaAg', 'travel')]
tmp$lg_travel <- log10(tmp$travel + 1)

tmp2 <- tmp
tmp <- tmp[tmp$Type != 'Ripar', ]

library(ggplot2)
#library(emmeans)
#asinTransform <- function(p) { asin(sqrt(p)) }
#logitTransform <- function(p) { log(p/(1-p)) }
theme_set(theme_bw())


tmp <- na.omit(tmp)
tmp2 <- na.omit(tmp2)

tmp2$Type <- ifelse(tmp2$Type == 'Ripar', 'Riparian',
                     ifelse(tmp2$Type == 'NRSur', 'NonRiparian-Surface',
                            ifelse(tmp2$Type == 'NRSubPd', 'NonRiparian-PD','NonRiparian-WD')))


tmp2$Type <- factor(tmp2$Type, levels = c('Riparian','NonRiparian-Surface','NonRiparian-PD','NonRiparian-WD'))
#levels(tmp2$Type) <- c('Ripar','NRSur','NRSubPd','NRSubWd')

# lm.mod <- lm(lg_travel ~ Type, data=tmp)
# anova(lm.mod)
# marginal <- emmeans(lm.mod, pairwise ~ Type)
# plot(marginal, comparisons = T)
# lsmip(lm.mod, lg_travel ~ Type)
# 
# library(FSA)
# tmp$Type <- as.factor(tmp$Type)
# kruskal.test(lg_travel ~ Type, data=tmp)



p <- ggplot(tmp2, aes(x=lg_travel, color=Type, fill=Type)) + 
  geom_density(alpha=.7) + 
  #geom_histogram(position='dodge', aes(y = ..density..)) + 
  #scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  #scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  
  scale_color_manual(values=c('#a6cee3','#1f78b4','#33a02c','#b2df8a')) +
  scale_fill_manual(values=c('#a6cee3','#1f78b4','#33a02c','#b2df8a')) +
  
  xlab('Magnitude - travel time (log[days])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots-20200128/travel_time-densitycurves.png', width = 8, height = 6)


p <- ggplot(tmp2, aes(x=lg_travel, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  xlab('Magnitude - travel time (log[days])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/travel_time.png', width = 8, height = 6)

p <- ggplot(tmp2, aes(x=lg_travel, color=Type, fill=Type)) + 
  geom_histogram(position='identity', aes(y = ..density..), bins=50) + 
  scale_color_manual(values=c('#a6cee3','#1f78b4','#33a02c','#b2df8a')) +
  scale_fill_manual(values=c('#a6cee3','#1f78b4','#33a02c','#b2df8a')) +
  xlab('Magnitude - travel time (log[days])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/travel_time--transparent-histogram.png', width = 8, height = 6, dpi=1000)

p <- ggplot(tmp, aes(x=lg_travel, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  xlab('Magnitude - travel time (log[days])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/travel_time.png')

tmp2$lg_ImpDrImperv <- log10(tmp2$ImpDrImperv + 0.01)
p <- ggplot(tmp2, aes(x=tr_ImpDrImperv, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  xlab('Mean % imperviousness in wetland basin (log10[%])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/drnimperv.png')

p <- ggplot(tmp2[tmp2$lg_ImpDrImperv > -2, ], aes(x=tr_ImpDrImperv, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  xlab('Mean % imperviousness in wetland basin (log10[%])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/drnimperv-no0s.png')

tmp2$lg_ImpDrAg <- log10(tmp2$ImpDrImperv + 0.01)
p <- ggplot(tmp2, aes(x=lg_ImpDrAg, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  xlab('% ag drainage in wetland basin (log10[%])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/drnagdrainage.png')

p <- ggplot(tmp2[tmp2$lg_ImpDrAg > -2, ], aes(x=lg_ImpDrAg, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4','#a6cee3')) +
  xlab('% ag drainage in wetland basin (log10[%])') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/drnagdrainage-no0s.png')


tmp$tr_ImpPaAg <- (tmp$ImpPaAg)^(1/4)
p <- ggplot(tmp, aes(x=tr_ImpPaAg, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  xlab('% ag drainage wetland path ([%]^1/4)') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/pthagdrain.png')

p <- ggplot(tmp[tmp$tr_ImpPaAg > 0, ], aes(x=tr_ImpPaAg, color=Type, fill=Type)) + 
  geom_histogram(position='dodge', aes(y = ..density..)) + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  xlab('% ag drainage wetland path ([%]^1/4)') + ylab('Density')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/pthagdrain-no0s.png')

x <- tmp %>% group_by(Type,ImpPaLev) %>% summarise(count=n()) %>% mutate(prop=(count/sum(count)))
p <- ggplot(x, aes(x=factor(ImpPaLev), y=prop, color=Type, fill=Type)) + 
  geom_bar(stat="identity", position='dodge') + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  #geom_vline(xintercept=1.5, linetype="dashed", color = "red", size=2) +
  xlab('Levee impact (0 = no, 1 = yes)') + ylab('Proportion')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/pthlevee.png')

x <- tmp %>% group_by(Type,ImpPaCan) %>% summarise(count=n()) %>% mutate(prop=(count/sum(count)))
p <- ggplot(x, aes(x=factor(ImpPaCan), y=prop, color=Type, fill=Type)) + 
  geom_bar(stat="identity", position='dodge') + 
  scale_color_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  scale_fill_manual(values=c('#33a02c','#b2df8a','#1f78b4')) +
  xlab('Canal impact (0 = no, 1 = yes)') + ylab('Proportion')
ggsave(file='D:/WorkFolder/WetlandConnectivity/Meetings/call-20190724/plots/pthcanal.png')






