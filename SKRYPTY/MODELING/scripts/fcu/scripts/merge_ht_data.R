library(plyr)
library(dplyr)
library(readxl)
library(stringr)
library(textclean)
        
setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/monitoring")

# replace Polish characters with latin
set_utf8 <- function(x) {
  # Declare UTF-8 encoding on all character columns:
  chr <- sapply(x, is.character)
  x[, chr] <- lapply(x[, chr, drop = FALSE], `Encoding<-`, "UTF-8")
  # Same on column names:
  Encoding(names(x)) <- "UTF-8"
  x
}
### change it to dbGetQuery, file is in repo :)
encoding_map = set_utf8(as.data.frame(read_excel("data/encoding.xlsx")))

ht_17_to_19 <- read_excel("data/holiday_tracker/HT_2017_2019_merged_filtered.xlsx")
ht_20 <- read_excel(paste("data/holiday_tracker/", format(Sys.time(), "%d%m%Y"), " HT.xlsx", sep=''))

# HT for 2020
ht_cols <- c("Role", "Team", "Employee", "Date")
ht_20_final <- data.frame(ht_20$Role, ht_20$Team, ht_20$Employee, ht_20$Date)
colnames(ht_20_final) <- ht_cols

### HT 2020 transformation ###
# Filtering data
ht_20_final <- ht_20_final[-which(is.na(ht_20_final$Team)),]
# ht_20_final <- ht_20_final[-which(is.na(ht_20_final$Employee)),]
ht_20_final <- ht_20_final[-which(ht_20_final$Team %in% c("Mgmt", "Process", "MI", "SME", "PMO")), ]

# format and reconcile date formatting
ht_17_to_19$Date <- as.POSIXct(substr(ht_17_to_19$Date, 1, 10), tz = 'UTC')
ht_20_final$Date <- as.POSIXct(substr(ht_20_final$Date, 1, 10), tz = 'UTC')

# Merge data from 2020 and previous year
holiday_tracker_all <- NULL
holiday_tracker_all <- bind_rows(ht_17_to_19, ht_20_final) %>% distinct()
holiday_tracker_all$Date <- as.POSIXct(substr(holiday_tracker_all$Date, 1, 10), tz = 'UTC')

# Change polish characters to ordinary characters
for(i in 1:nrow(holiday_tracker_all)){
  holiday_tracker_all$Employee[i] = mgsub(holiday_tracker_all$Employee[i],
                             pattern = encoding_map$pattern,
                             replacement = encoding_map$replacement)
}

holiday_tracker_all <- holiday_tracker_all %>% filter(!is.na(Employee))

write.csv(holiday_tracker_all, "data/holiday_tracker/ht_all_latin.csv", row.names=F)
