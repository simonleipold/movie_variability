
# Modified script for IS-RSA with Movie as a Random Effect

library(tidyverse)
library(lme4)
library(broom.mixed)

# Load functions to import data
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

# Set paths
behavior_path <- "dfs_behavior"
neural_path <- "dfs_neural"
control_path <- "dfs_control"
out_path <- "r_output_movie_random"
dir.create(out_path, showWarnings = FALSE)

# Load and prepare control and behavioral data
control_data <- load_csvs_control(control_path) %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_")) %>%
  pivot_wider(names_from = ControlVar, values_from = Distance)
control_data$Sex <- as.factor(control_data$Sex)

behavioral_data <- load_csvs_behavior(behavior_path) %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_")) %>%
  unite("TaskSession", Task, Session, sep = "_", remove = FALSE) %>%
  select(-c(Task,Session)) %>%
  pivot_wider(names_from = TaskSession, values_from = Distance)

# Load and prepare neural data
movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:210)
neural_data <- expand.grid(Movie = movies, Parcel = parcels) %>%
  pmap_df(~load_csvs_neural(neural_path, ..1, ..2)) %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

# Merge all data
all_data <- neural_data %>%
  inner_join(behavioral_data, by = c("Pair_Type", "combined_id", "Subject1", "Subject2")) %>%
  inner_join(control_data, by = c("Pair_Type", "combined_id", "Subject1", "Subject2"))

# Z-transform numeric predictors
all_data <- all_data %>%
  mutate(across(c(Age, Features_Pre, Features_Post, Naming_Pre, Naming_Post, Distance), scale)) %>%
  mutate(Sex = as.factor(Sex), Movie = as.factor(Movie), Parcel = as.factor(Parcel))

# Run LME model with Movie as a random effect for each parcel
lme_results_random_movie <- list()
for (parcel in unique(all_data$Parcel)) {
  df_parcel <- all_data %>% filter(Parcel == parcel)

  model_post <- lmer(Distance ~ Features_Post + Naming_Post + Age + Sex + 
                     (1 | Subject1) + (1 | Subject2) + (1 | Movie),
                     data = df_parcel, control = lmerControl(optimizer = "Nelder_Mead"))

  lme_results_random_movie[[parcel]] <- model_post

  print(paste("Finished", parcel))
}

# Save model list
# saveRDS(lme_results_random_movie, file = "lme4_models/lme_model_list_random_movie.rds")

# Format and write results
# Step 1: Extract raw result tibbles (without correcting yet)
results_list <- lapply(lme_results_random_movie, function(model) {
  tidy(model, effects = "fixed")
})
combined <- bind_rows(results_list, .id = "Parcel")

# Step 2: Filter all Features_Pre effects across all parcels
features_post_df <- combined %>%
  filter(term == "Features_Post") %>%
  rowwise() %>%
  mutate(pval = pt(statistic, df = 6216 - 5, lower.tail = FALSE))  # raw p

# Step 3: Apply global corrections
features_post_df <- features_post_df %>%
  ungroup() %>%
  mutate(pvalFDR = p.adjust(pval, method = "fdr"),
         pvalFWE = p.adjust(pval, method = "bonferroni")) %>%
  select(Parcel, estimate, statistic, pval, pvalFDR, pvalFWE)


write.table(features_post_df,
            file = file.path(out_path, "ISRSA_random_movie_Features_Post.csv"), sep = ",", row.names = FALSE)
