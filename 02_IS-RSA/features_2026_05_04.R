# ================================================================
# Visualize Feature score distributions by Fribble
# Session 2 only + feature-level sex differences
# ================================================================

library(tidyverse)

# ----------------------------------------------------------------
# Paths
# ----------------------------------------------------------------
base_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/MovVar_ImagNeuro_Revision01/distribution_features"

feature_file <- file.path(base_dir, "Feature_scores_all_participants_filtered.csv")

subject_file <- "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/subjectlist_age_sex.csv"

out_dir <- file.path(base_dir, "visualizations")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

# ----------------------------------------------------------------
# Theme
# ----------------------------------------------------------------
theme_CABB <- function(){
  theme_minimal() %+replace% 
    theme(
      plot.title = element_text(size = 20, hjust = 0.5),
      plot.subtitle = element_text(size = 20, hjust = 0.5),
      axis.title = element_text(size = 18),
      axis.text = element_text(size = 14),
      strip.text = element_text(size = 16),
      plot.margin = margin(t = 10, r = 10, b = 30, l = 10)
    )
}

# ----------------------------------------------------------------
# Read Features data: Session 2 only
# ----------------------------------------------------------------
features_raw <- read_csv(feature_file, show_col_types = FALSE) %>%
  mutate(
    PID = as.integer(PID),
    Session = as.integer(Session),
    Fribble = as.integer(Fribble),
    Feature = as.integer(Feature),
    Score = as.numeric(Score)
  ) %>%
  filter(Session == 2)

if (nrow(features_raw) == 0) {
  stop("No data found for Session 2.")
}

# ----------------------------------------------------------------
# Read subject list with age and sex
# ----------------------------------------------------------------
subjectlist <- read_csv(subject_file, show_col_types = FALSE) %>%
  mutate(
    PID = as.integer(PID),
    age = as.numeric(age),
    sex = as.integer(sex),
    sex_char = as.character(sex_char),
    sex_label = case_when(
      sex_char == "f" ~ "female",
      sex_char == "m" ~ "male",
      sex == 1 ~ "female",
      sex == 2 ~ "male",
      TRUE ~ NA_character_
    ),
    sex_label = factor(sex_label, levels = c("female", "male"))
  ) %>%
  distinct(PID, .keep_all = TRUE)

if (any(is.na(subjectlist$sex_label))) {
  stop("Some subjects have missing or unrecognized sex labels.")
}

write_csv(
  subjectlist %>% count(sex_label),
  file.path(out_dir, "sex_counts.csv")
)

# ----------------------------------------------------------------
# Check subject coverage
# ----------------------------------------------------------------
missing_subjects <- setdiff(subjectlist$PID, unique(features_raw$PID))
extra_subjects <- setdiff(unique(features_raw$PID), subjectlist$PID)

if (length(missing_subjects) > 0) {
  stop("Subjects missing from Session 2 Features data: ", paste(missing_subjects, collapse = ", "))
}

if (length(extra_subjects) > 0) {
  warning("Subjects in Session 2 Features data but not in subjectlist: ", paste(extra_subjects, collapse = ", "))
}

features <- features_raw %>%
  inner_join(subjectlist, by = "PID")

# ----------------------------------------------------------------
# Check completeness of Session 2 data
# ----------------------------------------------------------------
expected_grid <- expand_grid(
  PID = subjectlist$PID,
  Session = 2,
  Fribble = sort(unique(features$Fribble)),
  Feature = sort(unique(features$Feature))
)

missing_rows <- expected_grid %>%
  anti_join(features, by = c("PID", "Session", "Fribble", "Feature"))

duplicate_rows <- features %>%
  count(PID, Session, Fribble, Feature) %>%
  filter(n > 1)

if (nrow(missing_rows) > 0) {
  write_csv(missing_rows, file.path(out_dir, "missing_feature_rows_session2.csv"))
  stop("Some PID x Fribble x Feature combinations are missing for Session 2. See missing_feature_rows_session2.csv")
}

if (nrow(duplicate_rows) > 0) {
  write_csv(duplicate_rows, file.path(out_dir, "duplicate_feature_rows_session2.csv"))
  stop("Some PID x Fribble x Feature combinations are duplicated for Session 2. See duplicate_feature_rows_session2.csv")
}

message("All subjects have complete Session 2 Features data.")

# ----------------------------------------------------------------
# Add feature labels
# ----------------------------------------------------------------
feature_labels <- tibble(
  Feature = 1:29,
  Feature_label = c(
    "rounded",
    "pointy",
    "symmetrical",
    "elongated",
    "flat",
    "compact",
    "visually complex",
    "demanding attention",
    "characteristic color",
    "light/bright",
    "large",
    "small",
    "characteristic taste",
    "characteristic smell",
    "easily hearable",
    "related to movement",
    "human",
    "head/face",
    "body",
    "face/mouth actions",
    "hand/arm actions",
    "foot actions",
    "fixed place/location",
    "time relevant",
    "direct experience",
    "helps self/others",
    "surprising",
    "positive/pleasant",
    "negative/unpleasant"
  )
)

features_plot <- features %>%
  left_join(feature_labels, by = "Feature") %>%
  mutate(
    Feature_label = factor(Feature_label, levels = feature_labels$Feature_label),
    Fribble_label = factor(
      Fribble,
      levels = sort(unique(Fribble)),
      labels = paste("Fribble", sort(unique(Fribble)))
    )
  )

# ----------------------------------------------------------------
# Density plot: one panel per Feature, colored by Fribble
# ----------------------------------------------------------------
p_density <- ggplot(
  features_plot,
  aes(x = Score, color = Fribble_label, group = Fribble_label)
) +
  geom_density(linewidth = 0.8, adjust = 1.0) +
  facet_wrap(~ Feature_label, ncol = 5) +
  scale_x_continuous(limits = c(0, 100), breaks = c(0, 50, 100)) +
  labs(
    x = "Feature score",
    y = "Density"
  ) +
  theme_CABB() +
  theme(legend.position = "none")

ggsave(
  filename = file.path(out_dir, "Feature_score_distributions.png"),
  plot = p_density,
  width = 18,
  height = 15,
  dpi = 400
)

# ----------------------------------------------------------------
# Feature-level sex differences
# Scores averaged across Fribbles within each subject
# ----------------------------------------------------------------
features_subject_feature_mean <- features_plot %>%
  group_by(PID, sex_label, age, Feature, Feature_label) %>%
  summarise(
    Score = mean(Score, na.rm = TRUE),
    .groups = "drop"
  )

sex_tests_feature <- features_subject_feature_mean %>%
  group_by(Feature, Feature_label) %>%
  group_modify(~ {
    
    if (n_distinct(.x$sex_label) < 2 || min(table(.x$sex_label)) < 2) {
      return(tibble(
        n_female = sum(.x$sex_label == "female", na.rm = TRUE),
        n_male = sum(.x$sex_label == "male", na.rm = TRUE),
        mean_female = NA_real_,
        mean_male = NA_real_,
        diff_male_minus_female = NA_real_,
        t = NA_real_,
        df = NA_real_,
        p = NA_real_
      ))
    }
    
    test <- t.test(Score ~ sex_label, data = .x)
    
    mean_female <- mean(.x$Score[.x$sex_label == "female"], na.rm = TRUE)
    mean_male <- mean(.x$Score[.x$sex_label == "male"], na.rm = TRUE)
    
    tibble(
      n_female = sum(.x$sex_label == "female", na.rm = TRUE),
      n_male = sum(.x$sex_label == "male", na.rm = TRUE),
      mean_female = mean_female,
      mean_male = mean_male,
      diff_male_minus_female = mean_male - mean_female,
      t = unname(test$statistic),
      df = unname(test$parameter),
      p = test$p.value
    )
  }) %>%
  ungroup() %>%
  mutate(
    p_fdr = p.adjust(p, method = "fdr")
  ) %>%
  arrange(p_fdr)

write_csv(
  sex_tests_feature,
  file.path(out_dir, "sex_differences_by_feature_session2.csv")
)

# ----------------------------------------------------------------
# Optional visualization of feature-level sex differences
# ----------------------------------------------------------------
p_sex_diff <- ggplot(
  features_subject_feature_mean,
  aes(x = sex_label, y = Score)
) +
  geom_boxplot(outlier.shape = NA, width = 0.5) +
  geom_jitter(width = 0.12, alpha = 0.5, size = 1.2) +
  facet_wrap(~ Feature_label, ncol = 5) +
  scale_y_continuous(limits = c(-1, 101), breaks = seq(0, 100, 50)) +
  labs(
    x = "Sex",
    y = "Mean Feature score"
  ) +
  theme_CABB()
p_sex_diff

ggsave(
  filename = file.path(out_dir, "Feature_score_sex_differences.png"),
  plot = p_sex_diff,
  width = 18,
  height = 15,
  dpi = 400
)


message("Done. Outputs saved to: ", out_dir)
