# Summary -----------------------------------------------------------------
# Parcel-wise ISC variability and ISC-level correlation,
# controlled for parcel-wise tSNR

# Packages ----------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(broom)
library(rstatix)
library(ppcor)

# Prelude -----------------------------------------------------------------

movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:210)

# Directories
indir <- "dataframes"
tsnr_file <- file.path("csv_files", "parcel_tSNR_all_subjects_movies.csv")

outdir <- "r_output_anova_tSNR"
if (!dir.exists(outdir)) dir.create(outdir)

outdir_vis <- "visualizations"
if (!dir.exists(outdir_vis)) dir.create(outdir_vis)

# Brainnetome labels
labels <- read_csv(
  file = file.path(
    "/project/3011157.03/Simon/proj_2022_CABB_movie/",
    "MRI", "Brainnetome_atlas", "Brainnetome_labels_cortical.csv"
  )
)

# Theme -------------------------------------------------------------------

theme_CABB <- function(){
  theme_minimal() %+replace%
    theme(
      plot.title = element_text(size = 20, hjust = 0.5),
      plot.subtitle = element_text(size = 24, hjust = 0.5),
      axis.title = element_text(size = 18),
      axis.text = element_text(size = 14),
      strip.text = element_text(size = 16)
    )
}

# Read ISC data ------------------------------------------------------------

files_list <- expand.grid(movie = movies, parcel = parcels) %>%
  mutate(filename = paste0("ISCdf_upper_", movie, "_", parcel, ".csv")) %>%
  pmap(function(movie, parcel, filename) {
    file_path <- file.path(indir, filename)
    
    if (file.exists(file_path)) {
      read_csv(file_path, show_col_types = FALSE) %>%
        mutate(Movie = movie, Parcel = parcel)
    } else {
      NULL
    }
  })

combined_tibble <- bind_rows(files_list)

final_tibble <- combined_tibble %>%
  filter(Pair_Type == "Real") %>%
  mutate(
    Pair = paste(Subject1, Subject2, sep = "_"),
    Pair = as.factor(Pair),
    Movie = factor(Movie, levels = movies),
    Parcel = factor(Parcel, levels = parcels),
    FisherZ = 0.5 * log((1 + Correlation) / (1 - Correlation))
  )

# Parcel-wise repeated-measures ANOVA -------------------------------------

results <- final_tibble %>%
  group_by(Parcel) %>%
  anova_test(
    data = .,
    dv = FisherZ,
    wid = Pair,
    within = Movie
  )

# Extract F, p, and generalized eta-squared values
extracted_data <- list()

for (i in seq_along(results$anova)) {
  F_value <- results$anova[[i]]$ANOVA$F
  p_value <- results$anova[[i]]$ANOVA$p
  ges_value <- results$anova[[i]]$ANOVA$ges
  parcel_number <- i
  
  extracted_data[[i]] <- list(
    Parcel = parcel_number,
    Fval = F_value,
    p = p_value,
    ges = ges_value
  )
}

results_tibble <- bind_rows(extracted_data)

results_tibble <- results_tibble %>%
  mutate(
    pfwe = p.adjust(p, method = "bonferroni", n = length(extracted_data))
  )

# Join labels
results_tibble <- results_tibble %>%
  left_join(labels, by = c("Parcel" = "one_based")) %>%
  dplyr::select(-zero_based)

# Map Yeo_7network integers to network names
results_tibble <- results_tibble %>%
  mutate(Yeo_7network = case_when(
    Yeo_7network == 0 ~ "Other",
    Yeo_7network == 1 ~ "Visual",
    Yeo_7network == 2 ~ "Somatomotor",
    Yeo_7network == 3 ~ "Dorsal Attention",
    Yeo_7network == 4 ~ "Ventral Attention",
    Yeo_7network == 5 ~ "Limbic",
    Yeo_7network == 6 ~ "Frontoparietal",
    Yeo_7network == 7 ~ "Default",
    TRUE ~ as.character(Yeo_7network)
  ))

write.csv(
  results_tibble,
  file.path(outdir, "isc_anova.csv"),
  row.names = FALSE
)

# Read and aggregate tSNR --------------------------------------------------

tsnr_tibble <- read_csv(
  tsnr_file,
  col_types = cols(
    PID = col_character(),
    Movie = col_character(),
    zero_based = col_integer(),
    Parcel = col_integer(),
    label = col_character(),
    Yeo_7network = col_character(),
    Yeo_17network = col_character(),
    tSNR = col_double()
  )
)

# Mean tSNR per parcel across all subjects and movies
tsnr_parcel <- tsnr_tibble %>%
  group_by(Parcel) %>%
  summarise(
    tSNR_mean = mean(tSNR, na.rm = TRUE),
    tSNR_sd = sd(tSNR, na.rm = TRUE),
    tSNR_n = sum(!is.na(tSNR)),
    .groups = "drop"
  )

# ISC level, variability, and tSNR ----------------------------------------

corr_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  summarise(
    ISC = mean(FisherZ, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    Parcel = as.integer(str_remove(as.character(Parcel), "parcel"))
  ) %>%
  left_join(results_tibble, by = "Parcel") %>%
  left_join(tsnr_parcel, by = "Parcel") %>%
  drop_na(ISC, Fval, tSNR_mean)

# Partial correlation: ISC ~ Fval, controlling for tSNR --------------------

partial_test <- ppcor::pcor.test(
  x = corr_tibble$Fval,
  y = corr_tibble$ISC,
  z = corr_tibble %>% dplyr::select(tSNR_mean),
  method = "pearson"
)

partial_summary <- tibble(
  n = partial_test$n,
  covariates = partial_test$gp,
  df = partial_test$n - partial_test$gp - 2,
  partial_r = unname(partial_test$estimate),
  partial_R2 = unname(partial_test$estimate)^2,
  t = unname(partial_test$statistic),
  p = partial_test$p.value
)

print(partial_summary)

# Residuals only for plotting the adjusted association
lm_Fval_tsnr <- lm(Fval ~ tSNR_mean, data = corr_tibble)
lm_ISC_tsnr <- lm(ISC ~ tSNR_mean, data = corr_tibble)

corr_tibble <- corr_tibble %>%
  mutate(
    Fval_tSNR_resid = resid(lm_Fval_tsnr),
    ISC_tSNR_resid = resid(lm_ISC_tsnr)
  )

write_csv(
  corr_tibble,
  file.path(outdir, "Figure3D_tSNR_controlled.csv")
)

write_csv(
  partial_summary,
  file.path(outdir, "Figure3D_tSNR_controlled_partial_correlation.csv")
)

# Plot --------------------------------------------------------------------

correlation_plot_tsnr <- ggplot(
  corr_tibble,
  aes(x = Fval_tSNR_resid, y = ISC_tSNR_resid)
) +
  geom_point(color = "#1f77b4", size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "#ff7f0e") +
  theme_CABB() +
  labs(
    x = expression(paste("Variability (", italic(F), "), adjusted for tSNR")),
    y = "ISC, adjusted for tSNR"
  )

correlation_plot_tsnr

ggsave(
  filename = file.path(outdir_vis, "ANOVA_F_ISC_correlation_tSNR_controlled.png"),
  plot = correlation_plot_tsnr,
  dpi = 400,
  height = 5,
  width = 5,
  bg = "white"
)
