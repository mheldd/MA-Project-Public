library(dplyr)
library(ggplot2)
library(tidyr)
library(knitr)
library(patchwork)
library(tibble)

#clear workspace
rm(list = ls())

#run main file to get necessary functions and parameters
source("C:/Users/manue/OneDrive/Dokumente/MA/R/ma_main.R")


setwd("C:/Users/manue/PycharmProjects/MA/Py-Code/results_imp_res_multi")



###################
#Read and prepare data
##Plug in different betas for appendix

dur_values <- c(1, 10, 25, 150)
devact_values <- c(0, 1, 2, 3, 14)

# Generate all combinations
imp_res_data <- list()

for (dur in dur_values) {
  for (devact in devact_values) {
    if (dur == 150){
      if (devact == 14) {
        next
      }
        else {
            file_name <- paste0("a_0.125b_1e-05_devstrat_", devact, "_all.csv")
        }
    }
      else {
        file_name <- paste0("b_1e-05_dur_", dur, "_devact_", devact, "_all.csv")
      }
    
    data <- read.csv(file_name, header = FALSE)
    
    colnames(data) <- c("price_p1", "price_p2", "session_id", "num_periods")
    
    data$prof_1 <- profit(pricetrafo(data$price_p1), pricetrafo(data$price_p2))
    data$prof_2 <- profit(pricetrafo(data$price_p2), pricetrafo(data$price_p1))
    data$duration <- dur
    data$dev_action <- devact
    
    imp_res_data <- append(imp_res_data, list(data))
  }
}

###Find number of sessions ran
max_session_id <- max(imp_res_data[[1]]$session_id)

###################################################
##Plots/Figures for impulse response analysis

plot_data <- list()

for (data_file in imp_res_data){
  ##vectors of zeros to add aggregate data in
  agg_dev_p <- numeric(300)
  agg_nondev_p <- numeric(300)
  ##loop through sessions to aggregate data
  for (i in c(0 : max_session_id)){
    session_data <- filter(data_file, session_id == i)
    dev_p <- session_data[c(1:300), c(1)]
    nondev_p <- session_data[c(1:300), c(2)]
    agg_dev_p <- dev_p + agg_dev_p
    agg_nondev_p <- nondev_p + agg_nondev_p
  }

  ##create the resulting dataframe for plot
  df <- data.frame(
    mean_agg_dev = agg_dev_p/(max_session_id+1),
    mean_agg_nondev = agg_nondev_p/(max_session_id+1),
    Period = c(1:300)
  )
  nrow(data_file)
  nrow(df)
  
  ##transform data to long shape for plotting
  df_long <- pivot_longer(df, cols = c("mean_agg_dev", "mean_agg_nondev"), 
                          names_to = "Series", values_to = "Price")
  ##append transformed data to list
  plot_data <- append(plot_data, list(df_long))

}

###split in temporary and permanent deviation


plot_list <- list()
##Alternatively: coler = Series instead of linetype = Series c(2,5,6,11,7,12)
for (i in c(1:15)){
  plt <- ggplot(plot_data[[i]], aes(x = Period, y = Price, color = Series)) +
          geom_line(size = 1) +
          theme(legend.position = "none") +
          scale_x_continuous(name = "Period",
                             limits = c(145, 195),
                             breaks = seq(145, 195, by = 5),  # Positions for original data
                             labels = seq(-5, 45, by = 5)) + 
          ylim(0, 14) +
          labs(
            title = "",
            x = "Time",
            y = "Price"
          ) 
  plot_list <- append(plot_list, list(plt))
}

##first figure
    
setwd("C:/Users/manue/OneDrive/Dokumente/MA/Thesis_tex")
  
plot_list[[2]] + plot_list[[5]]

ggsave("imp_res_1.pdf", width=6, height=4)

plot_list_perm <- list()

for (i in c(16:19)){
  plt <- ggplot(plot_data[[i]], aes(x = Period, y = Price, color = Series)) +
    geom_line(size = 1) +
    theme(legend.position = "none") +
    scale_x_continuous(name = "Period",
                       limits = c(140, 290),
                       breaks = seq(140, 290, by = 10),  # Positions for original data
                       labels = seq(-10, 140, by = 10)) + 
    ylim(0, 14) +
    labs(
      title = "",
      x = "Time",
      y = "Price"
    ) 
  plot_list_perm <- append(plot_list_perm, list(plt))
}


##2nd figure
(plot_list[[7]] | plot_list[[12]]) / plot_list_perm[[2]]


###3rd figure
(plot_list[[11]] | plot_list[[12]]) /
  (plot_list[[13]] | plot_list[[14]])

ggsave("imp_res_3.pdf", width=6, height=4)



###appendix
(plot_list[[6]] | plot_list[[7]]) /
  (plot_list[[8]] | plot_list[[9]])

ggsave("imp_res_A1.pdf", width=6, height=4)

plot_list_perm[[1]] /
  plot_list_perm[[2]] /
  plot_list_perm[[3]] /
  plot_list_perm[[4]] 

ggsave("imp_res_A2.pdf", width=5, height=8)
  


  

  

########################################################################################################################
##Table on discounted profits before and after for both players
##

##Number of periods in that profits get evaluated after deviation
eval_length <- 150
  
profit_data <- list()


for (data_file in imp_res_data){
  if (data_file$dev_action[1] == 14){
    next
  }
  
  session_df <- data.frame(
    session_id = integer(),
    num_periods = integer(),
    prof_pre_dev = numeric(),
    prof_pre_nondev = numeric(),
    prof_post_dev = numeric(),
    prof_post_nondev = numeric(),
    prof_diff_dev = numeric(),
    prof_diff_nondev = numeric(),
    prof_rel_dev = numeric(),
    prof_rel_non_dev = numeric(),
    comp_prof = numeric(),
    duration = integer(),
    dev_action = integer(),
    periods_till_learn = integer(),
    better_off_dev = integer(),
    better_off_nondev = integer()
  )
  
  
  for (i in c(0:max_session_id)){
    session_data <- filter(data_file, session_id == i)
    
    pre <- session_data[1:eval_length,]
    post <- session_data[(eval_length+1):(2*eval_length),]
      
    #calculate discounted profits from list of prices over 150 periods pre and post deviation
    prof_pre_dev <- discount(profit(pricetrafo(pre$price_p1), pricetrafo(pre$price_p2)))
    prof_pre_nondev <- discount(profit(pricetrafo(pre$price_p2), pricetrafo(pre$price_p1)))
      
    prof_post_dev <- discount(profit(pricetrafo(post$price_p1), pricetrafo(post$price_p2)))
    prof_post_nondev <- discount(profit(pricetrafo(post$price_p2), pricetrafo(post$price_p1)))
    
    prof_diff_dev <- prof_post_dev - prof_pre_dev
    prof_diff_nondev <- prof_post_nondev - prof_pre_nondev
    
    prof_rel_dev <- prof_post_dev / prof_pre_dev
    prof_rel_nondev <- prof_post_nondev / prof_pre_nondev
    
    comp_prof <- prof_post_dev/prof_post_nondev
    
    if (prof_rel_dev > 1){
      better_off_dev = 1
    }
      else {
        better_off_dev = 0
      }
    
    if (prof_rel_nondev > 1){
      better_off_nondev = 1
    }
      else {
        better_off_nondev = 0
      }
    
    if (session_data$duration[1] == 150){
      periods_till_learn <- session_data$price_p1[2*eval_length+1]
    }
      else {
        periods_till_learn <- NA
      }
    
    session_df <- rbind(session_df, data.frame(session_id = session_data$session_id[1], num_periods = session_data$num_periods[1],
                                                 prof_pre_dev = prof_pre_dev, prof_pre_nondev = prof_pre_nondev, prof_post_dev = prof_post_dev,
                                                 prof_post_nondev = prof_post_nondev, prof_diff_dev = prof_diff_dev,
                                                 prof_diff_nondev = prof_diff_nondev, duration = session_data$duration[1],
                                                 dev_action = session_data$dev_action[1], periods_till_learn = periods_till_learn,
                                                 prof_rel_dev = prof_rel_dev, prof_rel_nondev = prof_rel_nondev, comp_prof = comp_prof,
                                                 better_off_dev = better_off_dev, better_off_nondev = better_off_nondev))
    
  }
  profit_data <- append(profit_data, list(session_df))
}


df_full <- data.frame(
  diff_dev = numeric(),
  diff_nondev = numeric(),
  rel_dev = numeric(),
  rel_nondev = numeric(),
  comp_prof = numeric(),
  better_off_dev = numeric(),
  better_off_nondev = numeric(),
  dev_act = integer(),
  dur = integer()
)

for (pd in profit_data){
  df_full <- rbind(df_full, data.frame(diff_dev = mean(pd$prof_diff_dev), diff_nondev = mean(pd$prof_diff_nondev),
                                       rel_dev = mean(pd$prof_rel_dev), rel_nondev = mean(pd$prof_rel_nondev), 
                                       comp_prof = mean(pd$comp_prof), better_off_dev = mean(pd$better_off_dev),
                                       better_off_nondev = mean(pd$better_off_nondev), dev_act = pd$dev_action[1],
                                       dur = pd$duration[1]))
}



df_full <- df_full[c(8, 9, 3, 4, 5, 6, 7)]


df_full <- df_full %>%
        add_column(n_sessions = 84, .after = "better_off_nondev")

c_names <- c("Action", "Periods", "$\\frac{\\Delta_{pre}^D}{\\Delta_{post}^D}$", 
             "$\\frac{\\Delta_{pre}^Q}{\\Delta_{post}^Q}$", 
             "$\\frac{\\Delta_{post}^D}{\\Delta_{post}^Q}$", 
             "$\\Delta_{post}^D > \\Delta_{pre}^D$", 
             "$\\Delta_{post}^Q > \\Delta_{pre}^Q$", "N")


kable(df_full, format = "latex", escape = FALSE, digits = 3, booktabs = TRUE, sep = "", align = "ll|cccccc",
      col.names = c_names, caption = "An example table caption.")


