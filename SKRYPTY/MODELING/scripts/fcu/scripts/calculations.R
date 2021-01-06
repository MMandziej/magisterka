library(plyr)
library(dplyr)
library(readxl)
library(stringr)

## Loading PostgreSQL driver
# drv <- dbDriver("PostgreSQL")
# 
# ## Connecting to db
# con <- dbConnect(drv,
#                  dbname = "lionqc",
#                  host = "40.121.134.61",
#                  port = 5432,
#                  user = "postgres",
#                  password = 'Mjord@n23')

setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/monitoring/data")

# Reading all cutoffs in the directory
files <- list.files(pattern = "cut off.xlsx", full.names = T)
cut_offs_all <- NULL
cut_offs_all <- sapply(files, read_excel, simplify=FALSE) %>% rbind.fill(.id = "id")

# Creating table on db and storing all cutoffs on that table
# dbWriteTable(con, "cutoff_all", cut_offs_all, row.names=FALSE)

ht_cols <- c("Role", "Team", "Employee", "Date")
# HT for 2020
ht_20 <- read_excel(paste("holiday_tracker/", format(Sys.time(), "%d%m%Y"), " HT.xlsx", sep=''))
ht_20_final <- data.frame(ht_20$Role, ht_20$Team, ht_20$Employee, ht_20$Date)
colnames(ht_20_final) <- ht_cols

# HT for 2018_2017
ht_17_18 <- read_excel("holiday_tracker/HT_2017_2018.xlsx")
ht_17_18_final <- data.frame(ht_17_18$CurrentRole, ht_17_18$TeamNo, ht_17_18$INGName, ht_17_18$CurrentDate)
colnames(ht_17_18_final) <- ht_cols

# # HT for 2019
ht_19 <- read_excel("holiday_tracker/HT.xlsx")
ht_19_final <- data.frame(ht_19$CurrentRole, ht_19$TeamNo,ht_19$INGName, ht_19$CurrentDate)
colnames(ht_19_final) <- ht_cols

# Creating names as they are in other ht files
#employee_name<-NULL
#for(i in 1:dim(ht_17_18_final)[1])
#{
#surname<- str_split(ht_17_18_final$Employee[i],",")[[1]][1]
#name<- str_split(ht_17_18_final$Employee[i],",")[[1]][2]
#name_final<- str_split(name," ")[[1]][2]
#name_first<- substr(name_final,1,1)
#emp_name<- paste(surname,","," ",name_first,"."," ","(",name_final,")",sep = "")

#employee_name <- rbind(employee_name,emp_name)
#}

#row.names(employee_name) <- NULL

#ht_17_18_final$Employee<-employee_name

## Binding all holiday tracker data into one df
holiday_tracker_all <- NULL
# holiday_tracker_all <- bind_rows(ht_17_18_final, ht_19_final, ht_20_final) %>% distinct()
holiday_tracker_all <- bind_rows(ht_17_19_final, ht_20_final) %>% distinct()
write.csv(holiday_tracker_all, "holiday_tracker/holiday_tracker_all.csv", row.names=F)

# # Data from past years
# ht_past <- NULL
# ht_past <- bind_rows(ht_17_18_final, ht_19_final) %>% distinct()
# # Filtering data
# ht_past <- ht_past[-which(is.na(ht_past$Team)),]
# ht_past <- ht_past[-which(is.na(ht_past$Employee)),]
# ht_past <- ht_past[-which(ht_past$Team %in% c("Mgmt", "Process", "MI", "SME", "PMO")), ]
# # format date
# ht_past$Date <- as.POSIXct(substr(ht_past$Date, 1, 10), tz = 'UTC')
# write.xlsx(ht_past, "holiday_tracker/HT_2017_2019_merged_filtered.xlsx", row.names=F)

# Creating new table on db and storing holiday_tracker_all
#dbWriteTable(con, "holiday_tracker_all", holiday_tracker_all)

# union data from 17/18 and 19 and replace polish characters
# holiday_tracker_17_19 <- bind_rows(ht_17_18_final, ht_19_final) %>% distinct()
# holiday_tracker_17_19 <- holiday_tracker_17_19[-which(is.na(holiday_tracker_17_19$Team)),]
# holiday_tracker_17_19 <- holiday_tracker_17_19[-which(is.na(holiday_tracker_17_19$Employee)),]
# holiday_tracker_17_19 <- filter(holiday_tracker_17_19, !Employee %in% c('xxxxxxxxxxxxx'))
# 
# for(i in 1:nrow(holiday_tracker_17_19)){
#   holiday_tracker_17_19$Employee[i] = mgsub(holiday_tracker_17_19$Employee[i],
#                                             pattern = encoding_map$pattern,
#                                             replacement = encoding_map$replacement)
# }
# 
# holiday_tracker_17_19$Date <- as.POSIXct(substr(holiday_tracker_17_19$Date, 1, 10), tz = 'UTC')
# write.csv(holiday_tracker_17_19, "holiday_tracker/ht_17_to_19_latin.csv", row.names=F)

