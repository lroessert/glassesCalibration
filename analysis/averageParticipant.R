library(readr)
library(knitr)
library(dplyr)

calibData <- read_delim("../all_calibrationSummary.tsv", delim = "\t")
kable(calibData, caption = 'Calibration Data, all subjects')

# group by unique conditions, and take the mean of all numeric columns
dat <- calibData %>%
  group_by(subj) %>%
  dplyr::filter(complete.cases(.))

dat <- dat %>%
  summarise_if(is.numeric, mean)

# drop the columns that are now irrelevant
dat <- dat %>%
  select(-one_of(c("trial", "ptIdx")))

# set condition and subj vars as factors
dat$subj <- factor(dat$subj)

# show a table
kable(dat, caption = 'Calibration data, mean by unique condition')
write.table(dat, file = '../calibrationSummary.tsv', quote = FALSE, sep = '\t', col.names = NA)