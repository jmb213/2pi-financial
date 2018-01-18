library("ggplot2")
library("dplyr")

mdata <- read.csv("base_data.csv")

# parse_day_int <- function(dt){
#   return(as.Date(
#     paste(substring(dt, 1, 4),
#           substring(dt, 5, 6),
#           substring(dt, 7, 8),sep="-")))
# }
# 
# mdata$date <- parse_day_int(mdata$obsDate)
# mdata$lagged_date <- c(mdata$date[-1], mdata$ndays[nrow(mdata)])
# 
# mdata <- mdata %>%
#   select(date, lagged_date, colorv, SPRealIndex)
# 
# mdata[mdata$lagged_date > Sys.Date(), "lagged_date"] <- Sys.Date()
# write.csv(mdata, "base_data.csv", row.names = FALSE)

mdata$date <- as.Date(mdata$date)
mdata$lagged_date <- as.Date(mdata$lagged_date)

mdata$period <- ifelse(mdata$colorv == 1, "other",
  ifelse(mdata$colorv == 2, "good", 
    ifelse(mdata$colorv == 3, "bad", 
    "best")))

color_palette <- c("other" = "purple", "good" = "green", "bad" = "red", "best" = "blue")

min_date <- min(mdata$date)
max_date <- max(mdata$date)  

ppp <- ggplot(mdata, aes(x = date, y = SPRealIndex)) +
  geom_rect(aes(fill = period, color = period,
    xmin = date, xmax = lagged_date), 
    ymin = -Inf, ymax = Inf, alpha=0.5) +
  geom_line(color="black") +
  scale_x_date(limits = c(min_date, max_date), expand = c(0,0)) +
  scale_fill_manual(values = color_palette) +
  scale_color_manual(values = color_palette) +
  labs(title='S&P 500 - Valuation and Future Returns', y='S&P 500 Real Index') +
  theme_bw() +
  theme(legend.position = "bottom", 
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank())