library(tidyverse)
library(lme4)
library(broom.mixed)

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
n_subj <- 178
n_pairs <- n_subj * (n_subj - 1) / 2   # 15753
k_fixed <- 2                           # intercept + BehaviorDistance
df_chen <- n_pairs - k_fixed           # 15751

# ------------------------------------------------------------------
# Load behavioral data (personality distance)
# ------------------------------------------------------------------
load_behavior <- function(path) {
  file_path <- file.path(path, "behavior_personality_df_full.csv")
  
  df <- read_csv(file_path) %>%
    rename(BehaviorDistance = Distance) %>%
    mutate(combined_id = paste(Subject1, Subject2, sep = "_"))
  
  return(df)
}

# ------------------------------------------------------------------
# Load neural data
# ------------------------------------------------------------------
load_neural <- function(path, movie, parcel) {
  file_path <- sprintf("%s/df_full_%s_%s.csv", path, movie, parcel)
  
  if (file.exists(file_path)) {
    df <- read_csv(file_path) %>%
      rename(NeuralDistance = Distance) %>%
      mutate(
        Movie = movie,
        Parcel = parcel,
        combined_id = paste(Subject1, Subject2, sep = "_")
      )
    return(df)
  } else {
    return(tibble())
  }
}

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
behavior_path <- "dfs_behavior"
neural_path <- "dfs_neural"

out_path <- "r_output_ISRSA"
if (!dir.exists(out_path)) {
  dir.create(out_path)
}

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
behavioral_data <- load_behavior(behavior_path)

movies <- paste0("movie", 1:14)
parcels <- paste0("parcel", 1:210)

neural_data <- expand.grid(Movie = movies, Parcel = parcels) %>%
  pmap_df(~load_neural(neural_path, ..1, ..2))

# ------------------------------------------------------------------
# Run IS-RSA (LME)
# ------------------------------------------------------------------
lme_results <- list()

for (movie in movies) {
  lme_results[[movie]] <- list()
}

for (movie in movies) {
  for (parcel in parcels) {
    
    tmp_neural <- neural_data %>%
      filter(Movie == movie, Parcel == parcel)
    
    if (nrow(tmp_neural) == 0) next
    
    tmp_ds <- inner_join(
      behavioral_data,
      tmp_neural,
      by = c("combined_id", "Subject1", "Subject2")
    )
    
    if (nrow(tmp_ds) == 0) next
    
    tmp_ds <- tmp_ds %>%
      mutate(across(c(BehaviorDistance, NeuralDistance), scale))
    
    model <- lmer(
      NeuralDistance ~ BehaviorDistance +
        (1 | Subject1) + (1 | Subject2),
      data = tmp_ds,
      control = lmerControl(optimizer = "Nelder_Mead")
    )
    
    lme_results[[movie]][[parcel]] <- model
    
    print(paste("Processed", movie, parcel))
  }
}

# ------------------------------------------------------------------
# Extract results
# ------------------------------------------------------------------
format_out <- function(results, df_model) {
  
  results_list <- lapply(results, function(model) {
    tidy(model, effects = "fixed")
  })
  
  combined_df <- bind_rows(results_list, .id = "Parcel")
  combined_df$Parcel <- gsub("[^0-9]", "", combined_df$Parcel)
  
  out_df <- combined_df %>%
    filter(term == "BehaviorDistance") %>%
    rowwise() %>%
    mutate(
      pval = pt(statistic, df = df_model, lower.tail = FALSE)
    )
  
  return(out_df)
}

pval_out <- function(res_df) {
  res_df$pvalFDR <- p.adjust(res_df$pval, method = "fdr")
  res_df$pvalFWE <- p.adjust(res_df$pval, method = "bonferroni")
  
  res_df <- res_df %>%
    select(Parcel, estimate, statistic, pval, pvalFDR, pvalFWE)
  
  return(res_df)
}

# ------------------------------------------------------------------
# Save results
# ------------------------------------------------------------------
movie_dfs <- list()

for (movie in names(lme_results)) {
  print(movie)
  movie_dfs[[movie]] <- format_out(lme_results[[movie]], df_model = df_chen)
}

for (movie in names(movie_dfs)) {
  result_df <- pval_out(movie_dfs[[movie]])
  
  file_name <- sprintf("%s/ISRSA_personality_%s.csv", out_path, movie)
  
  write.table(
    result_df,
    file = file_name,
    sep = ",",
    row.names = FALSE,
    quote = FALSE
  )
}

# save model list to file for later use (e.g., checking assumptions)
# lme_path = "lme4_models"
# if (!dir.exists(lme_path)) {
#   dir.create(lme_path)
# }
# saveRDS(lme_results, file = "lme4_models/lme_model_list_isrsa.rds")
