# Summary -----------------------------------------------------------------

# Run IS-RSA using linear mixed-effects models
# Schaefer 2018 atlas: 300 parcels, 17 networks


# Packages ----------------------------------------------------------------

library(tidyverse)
library(lme4)
library(broom.mixed)


# Prelude -----------------------------------------------------------------

project_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie"

main_out_dir <- file.path(
  project_dir,
  "Scripts",
  "MovVar_ImagNeuro_Revision01",
  "CABB_Schaefer"
)

behavior_path <- file.path(main_out_dir, "dfs_behavior")
control_path <- file.path(main_out_dir, "dfs_control")
neural_path <- file.path(main_out_dir, "dfs_neural")

stopifnot(dir.exists(behavior_path))
stopifnot(dir.exists(control_path))
stopifnot(dir.exists(neural_path))

out_path <- file.path(main_out_dir, "r_output_isrsa")
if (!dir.exists(out_path)) {
  dir.create(out_path, recursive = TRUE)
}

labels <- read_tsv(
  file = file.path(
    project_dir,
    "MRI",
    "Schaefer_atlas",
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_labels.tsv"
  ),
  show_col_types = FALSE
)

movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:300)

df_lme <- 6216 - 5


# Helper functions ---------------------------------------------------------

clean_subject_id <- function(x) {
  str_replace(as.character(x), "sub-", "") %>%
    str_pad(width = 3, side = "left", pad = "0")
}

load_csvs_behavior <- function(path) {
  file_list <- list.files(path, pattern = "df_full\\.csv", full.names = TRUE)
  
  map(file_list, ~{
    read_csv(.x, show_col_types = FALSE) %>%
      mutate(
        Subject1 = clean_subject_id(Subject1),
        Subject2 = clean_subject_id(Subject2),
        Task = ifelse(str_detect(.x, "Features"), "Features", "Naming"),
        Session = ifelse(str_detect(.x, "pre"), "Pre", "Post")
      )
  }) %>%
    bind_rows()
}

load_csvs_control <- function(path) {
  file_list <- list.files(path, pattern = "df_full\\.csv", full.names = TRUE)
  
  map(file_list, ~{
    read_csv(.x, show_col_types = FALSE) %>%
      mutate(
        Subject1 = clean_subject_id(Subject1),
        Subject2 = clean_subject_id(Subject2),
        ControlVar = ifelse(str_detect(.x, "age"), "Age", "Sex")
      )
  }) %>%
    bind_rows()
}

load_csvs_neural <- function(path, movie, parcel) {
  file_path <- file.path(path, sprintf("df_full_%s_%s.csv", movie, parcel))
  
  if (!file.exists(file_path)) {
    warning(paste("File does not exist:", file_path))
    return(tibble())
  }
  
  read_csv(file_path, show_col_types = FALSE) %>%
    mutate(
      Subject1 = clean_subject_id(Subject1),
      Subject2 = clean_subject_id(Subject2),
      Movie = movie,
      Parcel = parcel,
      combined_id = paste(Subject1, Subject2, sep = "_")
    )
}

add_corrected_pvals <- function(res_df) {
  res_df %>%
    mutate(
      Parcel = as.integer(Parcel),
      pvalFDR = p.adjust(pval, method = "fdr"),
      pvalFWE = p.adjust(pval, method = "bonferroni")
    ) %>%
    left_join(labels, by = c("Parcel" = "one_based")) %>%
    select(
      Parcel,
      label,
      Yeo_17_network,
      estimate,
      statistic,
      pval,
      pvalFDR,
      pvalFWE
    )
}


# Load control variables ---------------------------------------------------

control_data <- load_csvs_control(control_path) %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

wide_control_data <- control_data %>%
  pivot_wider(
    names_from = ControlVar,
    values_from = Distance
  ) %>%
  mutate(Sex = as.factor(Sex))


# Load behavioral data -----------------------------------------------------

behavioral_data <- load_csvs_behavior(behavior_path) %>%
  mutate(combined_id = paste(Subject1, Subject2, sep = "_"))

wide_behavioral_data <- behavioral_data %>%
  unite("TaskSession", Task, Session, sep = "_", remove = FALSE) %>%
  select(-c(Task, Session)) %>%
  pivot_wider(
    names_from = TaskSession,
    values_from = Distance
  )


# Run IS-RSA models --------------------------------------------------------

for (movie in movies) {
  
  message("Processing ", movie)
  
  movie_results <- list(
    features_pre = list(),
    features_post = list(),
    naming_pre = list(),
    naming_post = list()
  )
  
  for (parcel in parcels) {
    
    tmp_neural_ds <- load_csvs_neural(
      path = neural_path,
      movie = movie,
      parcel = parcel
    )
    
    if (nrow(tmp_neural_ds) == 0) {
      next
    }
    
    tmp_combined_ds <- wide_behavioral_data %>%
      inner_join(
        tmp_neural_ds,
        by = c("Pair_Type", "combined_id", "Subject1", "Subject2")
      ) %>%
      inner_join(
        wide_control_data,
        by = c("Pair_Type", "combined_id", "Subject1", "Subject2")
      ) %>%
      mutate(
        across(
          c(Age, Features_Pre, Features_Post, Naming_Pre, Naming_Post, Distance),
          ~ as.numeric(scale(.x))
        )
      )
    
    model_pre <- lmer(
      Distance ~ Features_Pre + Naming_Pre + Age + Sex +
        (1 | Subject1) + (1 | Subject2),
      data = tmp_combined_ds,
      control = lmerControl(optimizer = "Nelder_Mead")
    )
    
    model_post <- lmer(
      Distance ~ Features_Post + Naming_Post + Age + Sex +
        (1 | Subject1) + (1 | Subject2),
      data = tmp_combined_ds,
      control = lmerControl(optimizer = "Nelder_Mead")
    )
    
    parcel_num <- str_remove(parcel, "parcel")
    
    tidy_pre <- tidy(model_pre, effects = "fixed") %>%
      mutate(Parcel = parcel_num)
    
    tidy_post <- tidy(model_post, effects = "fixed") %>%
      mutate(Parcel = parcel_num)
    
    movie_results$features_pre[[parcel]] <- tidy_pre %>%
      filter(term == "Features_Pre")
    
    movie_results$features_post[[parcel]] <- tidy_post %>%
      filter(term == "Features_Post")
    
    movie_results$naming_pre[[parcel]] <- tidy_pre %>%
      filter(term == "Naming_Pre")
    
    movie_results$naming_post[[parcel]] <- tidy_post %>%
      filter(term == "Naming_Post")
    
    message("Processed ", movie, " ", parcel)
  }
  
  
  # Generate output for this movie -----------------------------------------
  
  message("Writing output for ", movie)
  
  for (effect in names(movie_results)) {
    
    result_df <- bind_rows(movie_results[[effect]]) %>%
      rowwise() %>%
      mutate(
        pval = pt(statistic, df = df_lme, lower.tail = FALSE)
      ) %>%
      ungroup() %>%
      add_corrected_pvals()
    
    file_name <- file.path(
      out_path,
      sprintf("ISRSA_%s_%s.csv", effect, movie)
    )
    
    write.table(
      result_df,
      file = file_name,
      sep = ",",
      row.names = FALSE,
      quote = FALSE
    )
  }
}

message("Finished Schaefer IS-RSA models.")
