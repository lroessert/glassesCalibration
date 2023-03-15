library(readr)
library(knitr)
library(dplyr)
library(lme4)
library(lmerTest)
library(lsmeans)
library(ggplot2)
library(ggpubr)
library(ggsignif)
# overall Accuracy plot
library(ggplot2)
library(ggpubr)
library(ggsignif)

ggsave <- function(...) {
  ggplot2::ggsave(...)
  invisible()
}

calibData <- read_delim("../all_calibrationSummary.tsv", delim = "\t")
kable(calibData[1:5,], caption = 'Calibration Data, all subjects')

# group by unique conditions, and take the mean of all numeric columns
dat <- calibData %>%
  group_by(subj, glasses, dist, offset) %>%
  na.omit()

dat <- dat %>% summarise_if(is.numeric, mean)


# drop the columns that are now irrelevant
dat <- dat %>% select(-one_of(c("trial", "ptIdx")))

# set condition and subj vars as factors
dat$subj <- factor(dat$subj)
dat$glasses <- factor(dat$glasses)
dat$dist <- factor(dat$dist)
dat$offset <- factor(dat$offset)

# show a table
kable(dat[1:5,], caption = 'Calibration data, mean by unique condition')

accMod.overall <- lmer(centDist ~ glasses + (1 | subj), data = dat)
summary(accMod.overall)

anova(accMod.overall)

lsmeans(accMod.overall, pairwise ~ glasses)

precMod.overall <- lmer(RMS ~ glasses + (1 | subj), data = dat)
summary(precMod.overall)

anova(precMod.overall)

lsmeans(precMod.overall, pairwise ~ glasses)

## Accuracy
accPlot <- ggplot(aes(y = centDist, x = glasses, fill = glasses),
                  data = dat) +
  geom_boxplot(aes(colour = "glasses")) +
  stat_summary(geom = "crossbar", fatten = 1, color = "white",
               fun.data = function(x) { return(c(y = median(x), ymin = median(x), ymax = median(x))) }) +
  labs(
    x = "Eye-tracker",
    y = "Error in Visual Angle (deg)",
    title = "Overall Accuracy"
  ) +
  scale_fill_manual("eye-tracker", values = c("#C26546", "#80422E", "#FF855C", "#402117")) +
  scale_colour_manual("eye-tracker", values = c("#C26546", "#80422E", "#FF855C", "#402117")) +
  scale_y_continuous(breaks = seq(0, 3, by = 1), expand = c(0, .1)) +
  theme(
    aspect.ratio = 1.5,
    panel.background = element_blank(),
    plot.title = element_text(hjust = .5, size = 14),
    axis.title = element_text(size = rel(1.3)),
    axis.text.x = element_text(size = rel(.8)),
    axis.text.y = element_text(size = rel(1.5)),
    axis.line.y = element_line(colour = "black", size = .5, linetype = "solid"),
    axis.ticks.x = element_blank(),
    panel.grid.major.y = element_line(colour = "darkgrey", linetype = "twodash", size = .25),
    legend.position = "none"
  ) +
  geom_segment(aes(x = .4, y = 0, xend = 4.6, yend = 0), size = .25)


## Precision
rmsPlot <- ggplot(aes(y = RMS, x = glasses, fill = glasses),
                  data = dat) +
  labs(
    x = "Eye-tracker",
    y = "Std. Dev. (deg)",
    title = "Overall Precision"
  ) +
  geom_boxplot(aes(colour = "glasses")) +
  stat_summary(geom = "crossbar", fatten = 1, color = "white",
               fun.data = function(x) { return(c(y = median(x), ymin = median(x), ymax = median(x))) }) +
  scale_fill_manual("eye-tracker", values = c("#C26546", "#80422E", "#FF855C", "#402117")) +
  scale_colour_manual("eye-tracker", values = c("#C26546", "#80422E", "#FF855C", "#402117")) +
  coord_cartesian(ylim = c(0, 1.5)) +
  scale_y_continuous(breaks = seq(0, 1.5, by = .2), expand = c(0, .03)) +
  theme(
    aspect.ratio = 1.5,
    panel.background = element_blank(),
    plot.title = element_text(hjust = .5, size = 14),
    axis.title = element_text(size = rel(1.3)),
    axis.text.x = element_text(size = rel(.8)),
    axis.text.y = element_text(size = rel(1.5)),
    axis.line.y = element_line(colour = "black", size = .5, linetype = "solid"),
    axis.ticks.x = element_blank(),
    panel.grid.major.y = element_line(colour = "darkgrey", linetype = "twodash", size = .25),
    legend.position = "none"
  ) +
  geom_segment(aes(x = .4, y = 0, xend = 4.6, yend = 0), size = .25) +
  geom_signif(y_position = 1.4, xmin = 1, xmax = 4, annotation = " ", tip_length = 0.01, size = 1)


## Combine plots
ggarrange(accPlot, rmsPlot,
          labels = c("A", "B"),
          ncol = 2, nrow = 1) +
  ggsave("../Figs/overallAccPrec_Outside.pdf", width = 8, height = 5) +
  ggsave("../Figs/overallAccPrec_Outside.png", width = 8, height = 5)

