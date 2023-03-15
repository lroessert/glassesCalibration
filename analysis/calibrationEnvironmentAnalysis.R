library(readr)
library(knitr)
library(dplyr)
library(lme4)
library(lmerTest)
library(lsmeans)
library(ggplot2)
library(ggpubr)
library(ggsignif)

ggsave <- function(...) {
  ggplot2::ggsave(...)
  invisible()
}

calibData <- read_delim("/Users/leonardrossert/Documents/User_Study/Results/analysis/All/all_calibrationSummary.tsv", delim = "\t")
kable(calibData[1:5,], caption = 'Calibration Data, all subjects')

# group by unique conditions, and take the mean of all numeric columns
dat <- calibData %>%
  group_by(subj, glasses, dist, offset, environment) %>%
  na.omit()

dat <- dat %>% summarise_if(is.numeric, mean)


# drop the columns that are now irrelevant
dat <- dat %>% select(-one_of(c("trial", "ptIdx")))

# set condition and subj vars as factors
dat$subj <- factor(dat$subj)
dat$glasses <- factor(dat$glasses)
dat$dist <- factor(dat$dist)
dat$offset <- factor(dat$offset)
dat$environment <- factor(dat$environment)

# show a table
kable(dat[1:5,], caption = 'Calibration data, mean by unique condition')

# build linear mixed effects model predicting accuracy (i.e. centDist)
accMod.overall <- lmer(centDist ~ environment + (1 | subj), data = dat)
summary(accMod.overall)

anova(accMod.overall)

lsmeans(accMod.overall, pairwise ~ environment)

# build linear mixed effects model predicting accuracy (i.e. centDist)
precMod.overall <- lmer(RMS ~ environment + (1 | subj), data = dat)
summary(precMod.overall)

anova(precMod.overall)

lsmeans(precMod.overall, pairwise ~ environment)

# overall Accuracy plot
library(ggplot2)
library(ggpubr)
library(ggsignif)

## Accuracy
accPlot <- ggplot(aes(y = centDist, x = environment, fill = environment),
                  data = dat) +
  geom_boxplot(aes(colour = "environment")) +
  stat_summary(geom = "crossbar", fatten = 1, color = "white",
               fun.data = function(x) { return(c(y = median(x), ymin = median(x), ymax = median(x))) }) +
  labs(
    x = "Environment",
    y = "Error in Visual Angle (deg)",
    title = "Overall Accuracy"
  ) +
  scale_fill_manual("environment", values = c("#C26546", "#80422E")) +
  scale_colour_manual("environment", values = c("#C26546", "#80422E")) +
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
rmsPlot <- ggplot(aes(y = RMS, x = environment, fill = environment),
                  data = dat) +
  labs(
    x = "Environment",
    y = "Std. Dev. (deg)",
    title = "Overall Precision"
  ) +
  geom_boxplot(aes(colour = "environment")) +
  stat_summary(geom = "crossbar", fatten = 1, color = "white",
               fun.data = function(x) { return(c(y = median(x), ymin = median(x), ymax = median(x))) }) +
  scale_fill_manual("environment", values = c("#C26546", "#80422E")) +
  scale_colour_manual("environment", values = c("#C26546", "#80422E")) +
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

  geom_signif(y_position = .95, xmin = 1, xmax = 2, annotation = "*", tip_length = 0.01, size = 1)


## Combine plots
ggarrange(accPlot, rmsPlot,
          labels = c("A", "B"),
          ncol = 2, nrow = 1) +
  ggsave("/Users/leonardrossert/Documents/User_Study/Results/analysis/Figs/overallAccPrec_Enviroment.pdf", width = 8, height = 5) +
  ggsave("/Users/leonardrossert/Documents/User_Study/Results/analysis/Figs/overallAccPrec_Environment.png", width = 8, height = 5)

