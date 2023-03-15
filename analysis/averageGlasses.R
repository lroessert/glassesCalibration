library(readr)
library(knitr)
library(dplyr)

calibData <- read_delim("/Users/leonardrossert/Documents/User_Study/Results/analysis/Glasses/all_AdHawk_Inside_calibrationSummary.tsv", delim = "\t")
kable(calibData, caption = 'Calibration Data, all subjects')

# group by unique conditions, and take the mean of all numeric columns
dat <- calibData %>%
  group_by(glasses) %>%
  na.omit()

dat <- dat %>% summarise_if(is.numeric, mean)

# drop the columns that are now irrelevant
dat <- dat %>%
  select(-one_of(c("trial", "ptIdx", "subj")))


# show a table
kable(dat, caption = 'Calibration data, mean by unique condition')
write.table(dat, file = '/Users/leonardrossert/Documents/User_Study/Results/analysis/Glasses/AdHawk_Inside_calibrationSummary.tsv', quote = FALSE, sep = '\t', col.names = NA)