# Summary -----------------------------------------------------------------

# Run a parcel-wise ANOVA to detect differences in ISC between movies
# for the Emofilm dataset

# Packages ----------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(ggpubr)
library(broom)
library(rstatix)
library(RColorBrewer)
library(ez)

# Prelude -----------------------------------------------------------------

# Define the range of movies and parcels
movies <- paste0("movie", 1:14)
parcels <- paste0("parcel", 1:210)

# Main project path
projpath <- "/project/3011157.03/Simon/proj_2022_CABB_movie"

# Get Brainnetome labels
labels <- read_csv(file = file.path(
  projpath,
  "MRI", "Brainnetome_atlas",
  "Brainnetome_labels_cortical.csv"
))

# Define directories
indir <- file.path(
  projpath,
  "Scripts", "MovVar_ImagNeuro_Revision01", "Emofilm", "dataframes"
)

outdir <- file.path(
  projpath,
  "Scripts", "MovVar_ImagNeuro_Revision01", "Emofilm", "r_output_anova"
)
if (!dir.exists(outdir)) {
  dir.create(outdir, recursive = TRUE)
}

outdir_vis <- file.path(
  projpath,
  "Scripts", "MovVar_ImagNeuro_Revision01", "Emofilm", "visualizations"
)
if (!dir.exists(outdir_vis)) {
  dir.create(outdir_vis, recursive = TRUE)
}

# Main --------------------------------------------------------------------

# Read all files into a list of tibbles
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

get_disjoint_pairs <- function(data, n_pairs = 14, seed = 123) {
  set.seed(seed)
  
  all_pairs <- data %>%
    distinct(Subject1, Subject2) %>%
    slice_sample(prop = 1)
  
  used_subjects <- c()
  selected_pairs <- tibble()
  
  for (i in seq_len(nrow(all_pairs))) {
    s1 <- all_pairs$Subject1[i]
    s2 <- all_pairs$Subject2[i]
    
    if (!(s1 %in% used_subjects) && !(s2 %in% used_subjects)) {
      selected_pairs <- bind_rows(selected_pairs, all_pairs[i, ])
      used_subjects <- c(used_subjects, s1, s2)
    }
    
    if (nrow(selected_pairs) == n_pairs) break
  }
  
  selected_pairs
}

selected_pairs <- get_disjoint_pairs(combined_tibble, 14)

filtered_tibble <- combined_tibble %>%
  semi_join(selected_pairs, by = c("Subject1", "Subject2"))

# Create a new column 'Pair' combining 'Subject1' and 'Subject2'
final_tibble <- filtered_tibble %>%
  mutate(Pair = paste(Subject1, Subject2, sep = "_")) %>%
  mutate(
    Pair = as.factor(Pair),
    Movie = as.factor(Movie),
    Parcel = as.factor(Parcel),
    FisherZ = 0.5 * log((1 + Correlation) / (1 - Correlation))
  )

# Perform within-subject ANOVA for each Parcel -----------------------------

run_aov_one_parcel <- function(df) {
  df <- droplevels(df)
  
  fit <- aov(FisherZ ~ Movie + Error(Pair / Movie), data = df)
  s <- summary(fit)
  
  subject_tab <- s[["Error: Pair"]][[1]]
  movie_tab   <- s[["Error: Pair:Movie"]][[1]]
  
  ss_subject <- subject_tab["Residuals", "Sum Sq"]
  ss_movie   <- movie_tab["Movie", "Sum Sq"]
  ss_error   <- movie_tab["Residuals", "Sum Sq"]
  
  tibble(
    DFn = movie_tab["Movie", "Df"],
    DFd = movie_tab["Residuals", "Df"],
    Fval = movie_tab["Movie", "F value"],
    p = movie_tab["Movie", "Pr(>F)"],
    ges = ss_movie / (ss_movie + ss_error + ss_subject)
  )
}

results_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  group_modify(~ run_aov_one_parcel(.x)) %>%
  ungroup() %>%
  mutate(
    Parcel = readr::parse_number(as.character(Parcel)),
    Fval = round(Fval, 3),
    ges = round(ges, 3)
  ) %>%
  select(Parcel, Fval, p, ges)

results_tibble <- results_tibble %>%
  mutate(pfwe = p.adjust(p, method = "bonferroni", n = nrow(results_tibble)))

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

# Define the path for the output file
output_file_path <- file.path(outdir, "isc_anova_emofilm.csv")

# Write the result tibble to a CSV file
write.csv(results_tibble, output_file_path, row.names = FALSE)

# Plotting ----------------------------------------------------------------

theme_CABB <- function() {
  theme_minimal() %+replace%
    theme(
      plot.title = element_text(size = 20, hjust = 0.5),
      plot.subtitle = element_text(size = 24, hjust = 0.5),
      axis.title = element_text(size = 18),
      axis.text = element_text(size = 14),
      strip.text = element_text(size = 16)
    )
}

# get parcels with high and low variability
high <- 76
low <- 111

# create tibble with selected parcels for plotting
plot_tibble <- final_tibble %>% 
  rename(ISC = FisherZ) %>% 
  filter(Parcel == paste0("parcel", high) | Parcel == paste0("parcel", low))

# Calculate mean and standard error for each movie
stats_summary <- plot_tibble %>%
  group_by(Movie, Parcel) %>%
  summarise(
    Avg = mean(ISC), 
    SE = sd(ISC) / sqrt(n()),  # Calculate standard error
    .groups = 'drop'
  )
stats_summary$MovieInt <- as.factor(as.integer(stats_summary$Movie))
stats_summary <- stats_summary %>%
  mutate(Parcel = factor(Parcel, levels = c("parcel76", "parcel111"),
                         labels = c("Superior Temporal Gyrus\n",
                                    "Parahippocampal Gyrus\n")))

# add movie and parcel info to original tibble (for dots plotting)
plot_tibble <- plot_tibble %>%
  mutate(MovieInt = as.factor(as.integer(Movie))) %>%
  mutate(Parcel = factor(Parcel, levels = c("parcel76", "parcel111"),
                         labels = c("Superior Temporal Gyrus\n",
                                    "Parahippocampal Gyrus\n")))

# Define the path for the output file
# output_file_path <- file.path(outdir, "FigureNotNeeded1.csv")

# Write the plot tibble to a CSV file
# write.csv(plot_tibble, output_file_path, row.names = FALSE)

# plot mean, se, and dots
plot_se_dots <- ggplot(stats_summary, aes(x = MovieInt, y = Avg, fill = Movie)) +
  geom_col(alpha = 1.0) +  # No transparency on bars
  geom_jitter(data = plot_tibble, 
              aes(x = MovieInt, y = ISC), 
              width = 0.15, 
              alpha = 0.8, 
              shape = 21, 
              color = "black", 
              # fill = "white",
              stroke = 0.3) +  # Overlayed points
  geom_errorbar(aes(ymin = Avg - SE, ymax = Avg + SE), width = 0.2) +
  labs(x = "Movie", y = "ISC") +
  scale_fill_manual(
    values = colorRampPalette(RColorBrewer::brewer.pal(8, "Dark2"))(
      n_distinct(stats_summary$Movie)
    )
  ) +
  # scale_fill_brewer(palette = "Dark2") +
  facet_wrap(~ Parcel) +
  theme_CABB() +
  guides(fill = "none")

# Print
plot_se_dots
# Save the plot
ggsave(filename = file.path(outdir_vis, "ANOVA_ISC_example_dots.png"), plot = plot_se_dots,
       dpi = 400, height = 6, width = 9, bg = "white")


## Whole brain-plot
whole_plot_tibble <- final_tibble %>% group_by(Pair, Movie) %>% 
  summarize(ISC_avg = mean(FisherZ))
# anova
library(ez)
ezANOVA(data = whole_plot_tibble, dv = ISC_avg, wid = Pair, within = Movie,
        type = 3)

capture.output(
  ezANOVA(data = whole_plot_tibble, dv = ISC_avg, wid = Pair, within = Movie,
          type = 3),
  file = file.path(outdir, "whole_brain_isc_anova.txt")
)
# Calculate mean and standard error for each movie
stats_summary <- whole_plot_tibble %>%
  group_by(Movie) %>%
  summarise(
    Avg = mean(ISC_avg), 
    SE = sd(ISC_avg) / sqrt(n()),  # Calculate standard error
    .groups = 'drop'
  )
stats_summary$MovieInt <- as.factor(as.integer(stats_summary$Movie))

# Add integer-coded Movie variable to the raw data
whole_plot_tibble <- whole_plot_tibble %>%
  mutate(MovieInt = as.factor(as.integer(Movie)))

# Define the path for the output file
# output_file_path <- file.path(outdir, "FigureNotNeeded2.csv")

# Write the plot tibble to a CSV file
# write.csv(whole_plot_tibble, output_file_path, row.names = FALSE)

# Plot mean, SE, and overlaid data points
plot_whole_se_dots <- ggplot(stats_summary, aes(x = MovieInt, y = Avg, fill = Movie)) +
  geom_col(alpha = 1.0) +  # No transparency for bars
  geom_jitter(data = whole_plot_tibble, 
              aes(x = MovieInt, y = ISC_avg), 
              width = 0.15, 
              alpha = 0.8, 
              shape = 21, 
              color = "black", 
              # fill = "white", 
              stroke = 0.3) +
  geom_errorbar(aes(ymin = Avg - SE, ymax = Avg + SE), width = 0.2) +
  labs(x = "Movie", y = "ISC") +
  scale_fill_manual(
    values = colorRampPalette(RColorBrewer::brewer.pal(8, "Dark2"))(
      n_distinct(stats_summary$Movie)
    )
  ) +
  # scale_fill_brewer(palette = "Dark2") +
  theme_CABB() +
  guides(fill = "none")

# Print the plot
plot_whole_se_dots

# Save the plot
ggsave(filename = file.path(outdir_vis, "ANOVA_ISC_whole_dots.png"), plot = plot_whole_se_dots,
       dpi = 400, height = 6, width = 7, bg = "white")

# Variability/level correlation -------------------------------------------

# get average ISC per parcel and join with variability

corr_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  summarize(ISC = mean(FisherZ))
corr_tibble$Parcel <- as.numeric(gsub("parcel", "", corr_tibble$Parcel))
corr_tibble <- corr_tibble %>%
  left_join(results_tibble, by = c("Parcel" = "Parcel")) %>% 
  select(-c(p, pfwe, Yeo_17network))
cor.test(corr_tibble$Fval, corr_tibble$ISC)
capture.output(
  cor.test(corr_tibble$Fval, corr_tibble$ISC),
  file = file.path(outdir, "isc_variability_correlation.txt")
)
# Define the path for the output file
output_file_path <- file.path(outdir, "Figure5D.csv")

# Write the plot tibble to a CSV file
write.csv(corr_tibble, output_file_path, row.names = FALSE)

correlation_plot <- ggplot(corr_tibble, aes(x = Fval, y = ISC)) +
  geom_point(color = '#1f77b4', size = 2) +  # Scatter plot
  geom_smooth(method = 'lm', se = TRUE, color = '#ff7f0e') +  # Add a linear regression line
  theme_CABB() +  # Use a minimal theme for better appearance
  labs(x = expression(Variability~(italic(F))), 
       y = "ISC")
correlation_plot
ggsave(filename = file.path(outdir_vis, "ANOVA_F_ISC_correlation.png"), plot = correlation_plot,
       dpi = 400, height = 5, width = 5, bg = "white")
