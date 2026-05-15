# Summary -----------------------------------------------------------------

# Run parcel-wise repeated-measures ANOVAs on ISC between movies,
# after residualizing FisherZ for pairwise average framewise displacement

# Packages ----------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(ggpubr)
library(broom)
library(rstatix)
library(ez)

# Prelude -----------------------------------------------------------------

# Define the range of movies and parcels
movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:210)

# Get Brainnetome labels
labels <- read_csv(file = file.path(
  "/project/3011157.03/Simon/proj_2022_CABB_movie/",
  "MRI", "Brainnetome_atlas",
  "Brainnetome_labels_cortical.csv"
))

# Define directories
indir <- "dataframes"

outdir <- "r_output_anova"
if (!dir.exists(outdir)) {
  dir.create(outdir)
}

outdir_vis <- "visualizations"
if (!dir.exists(outdir_vis)) {
  dir.create(outdir_vis)
}

fd_file <- file.path(
  "/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/MovVar_ImagNeuro_Revision01/control_motion",
  "framewise_displacement_by_subject_movie.csv"
)

# Helper functions ---------------------------------------------------------

format_pid <- function(x) {
  x <- as.character(x)
  x <- str_replace(x, "^sub-", "")
  x <- str_extract(x, "\\d+")
  paste0("sub-", sprintf("%03d", as.integer(x)))
}

residualize_with_mean <- function(y, x) {
  idx <- complete.cases(y, x)
  out <- rep(NA_real_, length(y))
  
  fit <- lm(y[idx] ~ x[idx])
  out[idx] <- residuals(fit) + mean(y[idx], na.rm = TRUE)
  
  out
}

# Main --------------------------------------------------------------------

# Read framewise displacement data
fd_tibble <- read_csv(fd_file, show_col_types = FALSE) %>%
  mutate(
    PID = format_pid(PID),
    Movie_nr = as.integer(Movie)
  ) %>%
  select(PID, Movie_nr, framewise_displacement)

# Read all ISC files into a list of tibbles
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

# Combine all tibbles into one tibble
combined_tibble <- bind_rows(files_list)

# Filter rows where Pair_Type is "Real"
filtered_tibble <- combined_tibble %>%
  filter(Pair_Type == "Real")

# Create final tibble and add pairwise average FD
final_tibble <- filtered_tibble %>%
  mutate(
    Pair = paste(Subject1, Subject2, sep = "_"),
    Subject1_fd_id = format_pid(Subject1),
    Subject2_fd_id = format_pid(Subject2),
    Movie_nr = as.integer(str_extract(Movie, "\\d+")),
    FisherZ = 0.5 * log((1 + Correlation) / (1 - Correlation))
  ) %>%
  left_join(
    fd_tibble %>% rename(fd_subject1 = framewise_displacement),
    by = c("Subject1_fd_id" = "PID", "Movie_nr" = "Movie_nr")
  ) %>%
  left_join(
    fd_tibble %>% rename(fd_subject2 = framewise_displacement),
    by = c("Subject2_fd_id" = "PID", "Movie_nr" = "Movie_nr")
  ) %>%
  mutate(
    framewise_displacement = rowMeans(
      cbind(fd_subject1, fd_subject2),
      na.rm = TRUE
    ),
    framewise_displacement = ifelse(
      is.nan(framewise_displacement),
      NA_real_,
      framewise_displacement
    ),
    Pair = as.factor(Pair),
    Movie = as.factor(Movie),
    Parcel = as.factor(Parcel)
  )

# Residualize FisherZ within each parcel using pairwise average FD
final_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  mutate(
    FisherZ_resid = residualize_with_mean(
      y = FisherZ,
      x = framewise_displacement
    )
  ) %>%
  ungroup()

# Perform within-subject ANOVA for each Parcel on residualized FisherZ
results <- final_tibble %>%
  group_by(Parcel) %>%
  anova_test(
    data = .,
    dv = FisherZ_resid,
    wid = Pair,
    within = Movie,
    type = 3
  )

# Extract ANOVA results ----------------------------------------------------

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

results_tibble <- dplyr::bind_rows(extracted_data)

# Apply Bonferroni correction for the p-values
results_tibble <- results_tibble %>%
  mutate(pfwe = p.adjust(p, method = "bonferroni", n = length(extracted_data)))

# Join labels
results_tibble <- results_tibble %>%
  left_join(labels, by = c("Parcel" = "one_based")) %>% 
  select(-zero_based)

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

# Write parcel-wise results
write.csv(
  results_tibble,
  file.path(outdir, "isc_anova_fd_residualized.csv"),
  row.names = FALSE
)

# Plotting ----------------------------------------------------------------

theme_CABB <- function(){
  theme_minimal() %+replace% 
    theme(
      plot.title = element_text(size = 20, hjust = 0.5),
      plot.subtitle = element_text(size = 20, hjust = 0.5),
      axis.title = element_text(size = 18),
      axis.text = element_text(size = 14),
      strip.text = element_text(size = 16)
    )
}

# Whole-brain ANOVA and plot ----------------------------------------------

whole_plot_tibble <- final_tibble %>%
  group_by(Pair, Movie) %>% 
  summarize(
    ISC_avg = mean(FisherZ_resid, na.rm = TRUE),
    .groups = "drop"
  )

# Whole-brain repeated-measures ANOVA on FD-residualized ISC
whole_anova <- ezANOVA(
  data = whole_plot_tibble,
  dv = ISC_avg,
  wid = Pair,
  within = Movie,
  type = 3
)

whole_anova

write.csv(
  as.data.frame(whole_anova$ANOVA),
  file.path(outdir, "isc_whole_brain_anova_fd_residualized.csv"),
  row.names = FALSE
)

# Calculate mean and standard error for each movie
stats_summary <- whole_plot_tibble %>%
  group_by(Movie) %>%
  summarise(
    Avg = mean(ISC_avg, na.rm = TRUE), 
    SE = sd(ISC_avg, na.rm = TRUE) / sqrt(sum(!is.na(ISC_avg))),
    .groups = "drop"
  )

stats_summary$MovieInt <- as.factor(as.integer(stats_summary$Movie))

# Add integer-coded Movie variable to the raw data
whole_plot_tibble <- whole_plot_tibble %>%
  mutate(MovieInt = as.factor(as.integer(Movie)))

# Write the plot tibble to a CSV file
write.csv(
  whole_plot_tibble,
  file.path(outdir, "Figure3A_fd_residualized.csv"),
  row.names = FALSE
)

# Plot mean, SE, and overlaid data points
plot_whole_se_dots <- ggplot(stats_summary, aes(x = MovieInt, y = Avg, fill = Movie)) +
  geom_col(alpha = 1.0) +
  geom_jitter(
    data = whole_plot_tibble, 
    aes(x = MovieInt, y = ISC_avg), 
    width = 0.15, 
    alpha = 0.8, 
    shape = 21, 
    color = "black",
    stroke = 0.3
  ) +
  geom_errorbar(aes(ymin = Avg - SE, ymax = Avg + SE), width = 0.2) +
  labs(x = "Movie", y = "FD-residualized ISC") +
  scale_fill_brewer(palette = "Dark2") +
  theme_CABB() +
  guides(fill = "none")

plot_whole_se_dots

ggsave(
  filename = file.path(outdir_vis, "ANOVA_ISC_whole_dots_fd_residualized.png"),
  plot = plot_whole_se_dots,
  dpi = 400,
  height = 6,
  width = 7,
  bg = "white"
)
