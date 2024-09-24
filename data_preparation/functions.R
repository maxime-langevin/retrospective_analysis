#setting graphs theme
theme_set(
  theme_classic() +
    theme(panel.grid.major.y = element_line(),
          text = element_text(family = "Times New Roman"),
          plot.title = element_text(face="bold")
    )
)


# Prepare reality data ----------------------------------------------------

#function to read data from Paireau et al  (2022) at a given geographical scale
f_read_paireau <- function(geographical_scale){
  
  temp <- readRDS("source_data/reality_Paireau_2022_paper/full_data.rds") %>%
    filter(
      region == geographical_scale 
    ) %>%
    select(
      date, 
      new_hosp = iHosp, #new hospitalizations
      new_hosp_smooth=iHosp_smooth, #new hospitalizations smoothed
      ICU_beds = inICU_smooth #ICU beds smoothed
    ) %>%
    distinct()
  
  #the "smooth" data is reported multiple time for each date, so we synthesize it
  temp <- temp %>%
    group_by(date) %>%
    summarise_all(mean, na.rm=T) %>%
    mutate_all(round, 0)
  
  return(temp)
}


# Save images and csv -----------------------------------------------------

#function to save pdf and png
f_save_graph_pdf_png <- function(path_name, graph_width, graph_height, dpi_resolution){
  #pdf
  ggsave(
    paste0(path_name, ".pdf"),
    width=graph_width, height=graph_height, bg="white", 
    device = cairo_pdf #devide cairo for Times New Roman font in pdf
  )
  #png
  ggsave(
    paste0(path_name, ".png"),
    width=graph_width, height=graph_height, bg="white", 
    dpi = dpi_resolution
  )
}

#function to save csv files in a directory. If directory does not exist, creates it
f_save_csv_files <- function(file_to_save, output_path, file_name){
  
  # Create the directory recursively if it doesn't exist
  if (!file.exists(output_path)) {
    dir.create(output_path, recursive = TRUE)
  }
  
  # Write the CSV file
  write_csv(file_to_save, file = file.path(output_path, file_name))
}


# Prepare and plot scenarios vs reality -----------------------------------

#function to plot scenarios vs reality
f_graph <- function(
    true_data, scenarios, # true_data: our reality dataset; #scenarios: modeler's scenario and reality data;
    true_data_variable,  # to select ICU or new hospitalizations in our true_data dataset
    publication_date, # publication date, indicated where vertical line should appear 
    y_label_publication_date, # where should the label "publication date" appear along the vertical axis
    x_min, x_max, y_max, # x and y limits of graph
    str_y, # label of the y axis (ICU beds or new hospitalizations)
    str_reality # source of our reality dataset (true_data)
){
  
  # get true data points in modelers' reports, to check if they match with our "reality" data
  modellers_true_data <- scenarios %>%
    select(date, reality)
  
  # get scenarios data in modelers' report
  scenarios <- scenarios %>%
    select(-reality) %>%
    gather(key=scenario, value = value, -date)
  
  # graph
  p <- ggplot(data = scenarios) + 
    
    #scenarios curves
    geom_line(
      aes(
        x=date, y=value, 
        group=scenario, color="scenarios"
      ),
      size = 1
    ) + 
    
    # reality curve
    geom_line(
      data= true_data, 
      aes(
        x=date, y=!!as.symbol(true_data_variable), 
        color = str_reality
      ),
      size = 1
    ) +
    
    # modelers reality points
    geom_point(
      data = modellers_true_data,
      aes(
        date, reality, color = "reality in report"
      ) 
    ) +
    
    # publication date line and label
    geom_vline(
      xintercept = as.Date(publication_date), linetype="dashed"
    ) +
    annotate(
      'text', x = as.Date(publication_date)-1, y = y_label_publication_date, label = "publication\ndate", 
      color = "black", fontface = "italic", family = "Times New Roman", hjust=1
    ) +
    
    # graph x and y limits
    xlim(as.Date(x_min), as.Date(x_max)) + ylim(0, y_max) + 
    
    # other options
    g_theme +
    labs(
      title = "",
      subtitle = "",
      color="",
      x="", y= str_y
    )
  
  return(p)
}


# gathers in one same dataset scenarios, our reality data, and modeler's reality data
f_prepare_to_save <- function(
    dataset_scenarios, # scenarios data, which also contains modelers' reality data
    dataset_reality, # our reality data
    variable_select # to select ICU or new hospitalization in our reality dataset
){
  
  # reality from in reality dataset 
  temp_reality <- dataset_reality %>% select(date, reality = !!as.symbol(variable_select))
  
  # reality in modeler's report
  temp_reality_report <- dataset_scenarios %>% select(date, reality_report = reality)
  
  # x and y offset in modeler's scenarios
  temp_scenarios <- dataset_scenarios %>% select(-reality)
  
  temp <- full_join(temp_scenarios, temp_reality_report, by="date")
  temp <- left_join(temp, temp_reality)
  
  return(temp)
}


#function to extract med, min and max scenarios, and compute their relative errors to reality in %. Adds them 6 to the original dataset.
f_compute_error <- function(
    date_begin, date_end, # dates delimiting the comparison period
    dataset, # dataset to use 
    normalization_value # we normalize the error by the maximum value of ICU beds or new hospitalizations over the period
){
  
  #dates delimiting the comparison period
  date_min <- as.Date(date_begin)
  date_max <- as.Date(date_end)
  
  #preparing file : gets date and true data value on the period
  reality_file <- dataset %>%
    select(date, reality) %>%
    filter(date>date_min & date<date_max)
  
  #computing min, med and max of scenarios
  temp <- dataset %>% 
    select(-reality, -reality_report) %>%
    rowwise() %>%
    mutate(
      med = median(c_across(-date), na.rm=T),
      min = min(c_across(-date), na.rm=T),
      max = max(c_across(-date), na.rm=T)
    )
  
  #joins 2 files
  reality_file <- inner_join(reality_file, temp, by="date")
  reality_file <- reality_file %>%
    mutate(
      error_min = round((min-reality)/normalization_value*100, 1),
      error_med = round((med-reality)/normalization_value*100, 1),
      error_max = round((max-reality)/normalization_value*100, 1)
    ) %>%
    
    #remove infinite values (when min med and max applied to NAs)
    filter(
      !(is.infinite(min) | is.infinite(med) | is.infinite(max))
    )
  
  return (reality_file)
}


#function to plot relative errors
f_graph_error <- function(
    dataset, # dataset to use
    publication_date, # for vertical line indicating publication date
    y_label # where should the label "publication date" appear along the vertical axis
){
  
  #graph
  ggplot(
    dataset, aes(date)
  ) + 
    
    # line indicating median scenario 
    geom_line(
      aes(y=error_med)
    ) +
    
    # area indicating min and max scenarios around median line
    geom_ribbon(
      aes(ymin = error_min, ymax = error_max), alpha = 0.1
    ) + 
    
    # to indicate 0% error
    geom_hline(yintercept = 0) +
    
    # vertical line to indicate publication date, and its label
    geom_vline(
      xintercept=as.Date(publication_date), linetype="dashed"
    ) +
    annotate(
      'text', x = as.Date(publication_date)-1, y = y_label, label = "publication\ndate", 
      color = "black", fontface = "italic", family = "Times New Roman", hjust=1
    ) +
    
    #labels
    labs(
      x="", y="error as % of 1st wave peak",
      title = "Median, min and max relative errors of scenarios vs reality",
      subtitle = "line: median scenario ; area: min and max scenarios"
    )
}



# Prepare and plot results ------------------------------------------------

# read all the prepared ICU files (scenarios + reality)
f_read_ICU <- function(date_scenario){
  
  #get scenario data, add report ID
  data <- read_csv(
    paste0(path_source, "ICU_scenarios/", date_scenario, "_ICU.csv")
  ) %>% 
    mutate(report = gsub("_", "-", date_scenario))
  
  #get last date of reality data in report
  temp <- data %>% select(date, reality_report) %>%
    filter(is.na(reality_report)==F)
  begin_date <- max(temp$date)
  
  #keep only data after this date
  data <- data %>%
    filter(date>=begin_date)
  
  return(data)
}

# read all the prepared new hosp files (scenarios + reality)
f_read_new_hosp <- function(date_scenario){
  #get scenario data, add report ID
  data <- read_csv(
    paste0(path_source, "new_hosp_scenarios/", date_scenario, "_new_hosp.csv")
  ) %>% 
    mutate(report = gsub("_", "-", date_scenario))
  
  #get last date of reality data in report
  temp <- data %>% select(date, reality_report) %>%
    filter(is.na(reality_report)==F)
  begin_date <- max(temp$date)
  
  #keep only data after this date
  data <- data %>%
    filter(date>=begin_date)
}

# compute error relative to max ICU or new hosp occupancy (used for colored scenarios in graph)
f_gather_scenarios_compute_relative_error <- function(dataset, max_value){
  
  temp <- dataset %>%
    
    #gather all scenarios values in 1 column, our official reality in another column
    select(-reality_report) %>%
    gather(scenario_type, value, -c(date, report, reality)) %>%
    
    #compute relative error
    mutate(
      error = round((value-reality)/max_value*100)
    ) 
  
  return(temp)
}
