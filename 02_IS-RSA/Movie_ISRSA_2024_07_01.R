library(tidyverse)
library(lme4)
library(broom.mixed)

# Function to load all CSVs from a directory and add additional columns based on file name
load_csvs_behavior <- function(path) {
  file_list <- list.files(path, pattern = "df_full\\.csv", full.names = TRUE)
  df_list <- map(file_list, ~{
    df <- read_csv(.x)
    df <- df %>% 
      mutate(Task = ifelse(str_detect(.x, "Features"), "Features", "Naming"),
             Session = ifelse(str_detect(.x, "pre"), "Pre", "Post"))
    return(df)
  }) %>%
    bind_rows()
  return(df_list)
}
# Function to load all CSVs from a directory and add additional columns based on file name
load_csvs_control <- function(path) {
  file_list <- list.files(path, pattern = "df_full\\.csv", full.names = TRUE)
  df_list <- map(file_list, ~{
    df <- read_csv(.x)
    df <- df %>% 
      mutate(ControlVar = ifelse(str_detect(.x, "age"), "Age", "Sex"))
    return(df)
  }) %>%
    bind_rows()
  return(df_list)
}

# Function to load neural CSVs and add columns for Movie and Parcel
load_csvs_neural <- function(path, movie, parcel) {
  file_path <- sprintf("%s/df_full_%s_%s.csv", path, movie, parcel)
  if (file.exists(file_path)) {
    df <- read_csv(file_path)
    df <- df %>% 
      mutate(Movie = movie, Parcel = parcel)
    return(df)
  } else {
    return(tibble())
  }
}

# Paths to directories
behavior_path <- "dfs_behavior"
neural_path <- "dfs_neural"
control_path <- "dfs_control"

out_path <- "r_output"
if (!dir.exists(out_path)) {
  dir.create(out_path)
}

# Load control variables
control_data <- load_csvs_control(control_path)

# Add a combined identifier column sorted to ensure consistent pair naming
control_data <- control_data %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

# Convert from long to wide format
wide_control_data <- control_data %>%
  pivot_wider(
    names_from = ControlVar,  # Use the new TaskSession as the source of new column names
    values_from = Distance     # Fill the new columns with values from the Distance column
  )
wide_control_data$Sex <- as.factor(wide_control_data$Sex)

# Load behavioral data
behavioral_data <- load_csvs_behavior(behavior_path)

# Add a combined identifier column sorted to ensure consistent pair naming
behavioral_data <- behavioral_data %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

# Convert from long to wide format
wide_behavioral_data <- behavioral_data %>%
  unite("TaskSession", Task, Session, sep = "_", remove = FALSE) %>%  # Create a new combined column for pivot
  select(-c(Task,Session)) %>% 
  pivot_wider(
    names_from = TaskSession,  # Use the new TaskSession as the source of new column names
    values_from = Distance     # Fill the new columns with values from the Distance column
  )

# Load neural data
movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:210)
neural_data <- expand.grid(Movie = movies, Parcel = parcels) %>%
  pmap_df(~load_csvs_neural(neural_path, ..1, ..2))

neural_data <- neural_data %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

# Run IS-RSA using linear mixed-effects models ----------------------------

# Initialize an empty list for LME results
lme_results <- list()

# Create an empty list for each movie
for (movie in movies) {
  lme_results[[movie]] <- list()
}

# Nested loop through each movie and parcel
for (movie in movies) {
  for (parcel in parcels) {
    
    # Create a temporary neural ds
    tmp_neural_ds <- neural_data %>% filter(Movie == movie) %>% 
      filter(Parcel == parcel)
    
    # Create a temporary combined ds
    tmp_combined_ds <- inner_join(wide_behavioral_data, tmp_neural_ds,
                                  by = c("Pair_Type", "combined_id", 
                                         "Subject1", "Subject2"))
    
    # Create a temporary combined ds with control variables
    tmp_combined_ds <- inner_join(wide_control_data, tmp_combined_ds,
                                  by = c("Pair_Type", "combined_id", 
                                         "Subject1", "Subject2"))
    
    # Z-transform the specified columns
    tmp_combined_ds <- tmp_combined_ds %>%
      mutate(across(c(Age, Features_Pre, Features_Post, 
                      Naming_Pre, Naming_Post, Distance), scale))
    
    # Run mixed model for Pre variables
    model_pre <- lmer(Distance ~ Features_Pre + Naming_Pre + Age + Sex +
                      (1|Subject1) + (1|Subject2), 
                      data = tmp_combined_ds, 
                      control = lmerControl(optimizer ="Nelder_Mead"))
    
    # Run mixed model for Post variables
    model_post <- lmer(Distance ~ Features_Post + Naming_Post + Age + Sex +
                       (1|Subject1) + (1|Subject2), 
                       data = tmp_combined_ds, 
                       control = lmerControl(optimizer ="Nelder_Mead"))
    
    # Add LME results to the list, using separate sub-lists for pre and post models
    lme_results[[movie]][[paste(parcel, "pre", sep = "_")]] <- model_pre
    lme_results[[movie]][[paste(parcel, "post", sep = "_")]] <- model_post
    
    # Print statement to track progress (optional)
    print(paste("Processed", movie, parcel, "models: pre and post"))
  }
}


# Generate output ---------------------------------------------------------

# Function to collect and reformat LME results, calculate p-values
format_out <- function(results, model_type) {
  # Generate a single tibble containing LME results
  results_list <- lapply(results, function(model) {
    tidy(model, effects = "fixed")
  })
  combined_df <- bind_rows(results_list, .id = "Parcel")
  
  # Update Parcel names to retain only numeric parts and the model type
  combined_df$Parcel <- gsub("[^0-9]", "", combined_df$Parcel)
  
  # select features pre
  features_pre_df <- combined_df %>% filter(term == "Features_Pre")
  # add p values based on t statistic and fixed degrees of freedom
  features_pre_df <- features_pre_df %>%
    rowwise() %>%
    mutate(pval = pt(statistic, df = 6216 - 5, lower.tail = FALSE))
  # select features post
  features_post_df <- combined_df %>% filter(term == "Features_Post")
  # add p values based on t statistic and fixed degrees of freedom
  features_post_df <- features_post_df %>%
    rowwise() %>%
    mutate(pval = pt(statistic, df = 6216 - 5, lower.tail = FALSE))
  # select naming pre
  naming_pre_df <- combined_df %>% filter(term == "Naming_Pre") 
  # add p values based on t statistic and fixed degrees of freedom
  naming_pre_df <- naming_pre_df %>%
    rowwise() %>%
    mutate(pval = pt(statistic, df = 6216 - 5, lower.tail = FALSE))
  # select naming post
  naming_post_df <- combined_df %>% filter(term == "Naming_Post") 
  # add p values based on t statistic and fixed degrees of freedom
  naming_post_df <- naming_post_df %>%
    rowwise() %>%
    mutate(pval = pt(statistic, df = 6216 - 5, lower.tail = FALSE))
  
  return(list(features_pre_df, features_post_df, naming_pre_df, 
              naming_post_df))
}

## function to calculate FDR and FWE-adjusted p-values
pval_out <- function(res_df) {
  res_df$pvalFDR <- p.adjust(res_df$pval, method = "fdr") # FDR
  res_df$pvalFWE <- p.adjust(res_df$pval, method = "bonferroni") # FWE
  res_df <- res_df %>% select(Parcel, estimate, statistic, pval, pvalFDR, pvalFWE)
  return(res_df)
}

# Applying the function to each movie in the lme_results list
movie_dfs <- list()
for (movie in names(lme_results)) {
  print(movie)
  movie_dfs[[movie]] <- format_out(lme_results[[movie]])
}

# Loop through each movie and effect to apply pval_out and write to CSV
effects <- c("features_pre", "features_post", "naming_pre", "naming_post")
for (movie in names(movie_dfs)) {
  for (i in seq_along(effects)) {
    # Calculate p-values
    result_df <- pval_out(movie_dfs[[movie]][[i]])
    
    # Construct file name based on movie and effect
    file_name <- sprintf("%s/ISRSA_%s_%s.csv", out_path, effects[i], movie)
    
    # Write to CSV
    write.table(result_df, file = file_name, sep = ",", row.names = FALSE, quote = FALSE)
  }
}

# save model list to file for later use (e.g., checking assumptions)
saveRDS(lme_results, file = "lme4_models/lme_model_list_isrsa.rds")
