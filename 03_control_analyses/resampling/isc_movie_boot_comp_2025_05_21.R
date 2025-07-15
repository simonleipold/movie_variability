
# Summary -----------------------------------------------------------------

# Run a whole-brain bootstrap test to detect differences in ISC between movies

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
labels <- read_csv(file = file.path("/project/3011157.03/Simon/proj_2022_CABB_movie/",
                                    "MRI", "Brainnetome_atlas",
                                    "Brainnetome_labels_cortical.csv"))

# Define directories
indir = "dataframes"
outdir = "r_output_anova"
if (!dir.exists(outdir)) {
  dir.create(outdir)
}
outdir_vis = "visualizations"
if (!dir.exists(outdir_vis)) {
  dir.create(outdir_vis)
}

# Main --------------------------------------------------------------------

# Read all files into a list of tibbles
files_list <- expand.grid(movie = movies, parcel = parcels) %>%
  mutate(filename = paste0("ISCdf_upper_", movie, "_", parcel, ".csv")) %>%
  pmap(function(movie, parcel, filename) {
    file_path <- file.path(indir, filename)  # Specify your directory where files are stored
    if (file.exists(file_path)) {
      read_csv(file_path) %>%
        mutate(Movie = movie, Parcel = parcel)
    } else {
      NULL  # Return NULL if file does not exist
    }
  })

# Combine all tibbles into one tibble
combined_tibble <- bind_rows(files_list)

# Create a new column 'Pair' combining 'Subject1' and 'Subject2'
final_tibble <- combined_tibble %>%
  mutate(Pair = paste(Subject1, Subject2, sep = "_")) %>%
  mutate(
    Pair = as.factor(Pair),
    Movie = as.factor(Movie),
    Parcel = as.factor(Parcel),
    FisherZ = 0.5 * log((1 + Correlation) / (1 - Correlation))
  )

# === Parameters ===
n_iter <- 1000
n_pairs <- 56
alpha <- 0.05
movie_levels <- unique(final_tibble$Movie)

# === Helper to sample disjoint subject pairs ===
get_disjoint_pairs <- function(pair_df, n_pairs) {
  all_pairs <- pair_df %>% distinct(Subject1, Subject2, Pair)
  all_pairs <- all_pairs[sample(nrow(all_pairs)), ]  # true random shuffle
  
  used_subjects <- character()
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
  
  if (nrow(selected_pairs) < n_pairs) return(NULL)
  return(selected_pairs)
}
## Whole-brain ANOVA
# === Main loop: resample disjoint pairs and run ANOVA ===
set.seed(42)
f_values <- numeric(n_iter)
f_list <- list()

for (i in 1:n_iter) {
  pairs_drawn <- get_disjoint_pairs(final_tibble, n_pairs)
  if (is.null(pairs_drawn)) {
    message(sprintf("Iteration %d: Not enough disjoint pairs.", i))
    f_values[i] <- NA
    next
  }
  
  # Filter for selected pairs
  data_subset <- final_tibble %>%
    filter(Pair %in% pairs_drawn$Pair) %>%
    group_by(Pair, Movie) %>%
    summarise(ISC = mean(FisherZ), .groups = "drop")
  
  # Run repeated-measures ANOVA
  result <- tryCatch({
    ezANOVA(
      data = data_subset,
      dv = ISC,
      wid = Pair,
      within = Movie,
      type = 3,
      detailed = TRUE
    )
  }, error = function(e) NULL)
  
  movie_stats <- tryCatch({
    result$ANOVA %>% filter(Effect == "Movie")
  }, error = function(e) NULL)
  
  if (!is.null(movie_stats) && nrow(movie_stats) == 1) {
    f_list[[i]] <- movie_stats
    f_values[i] <- movie_stats$F
  } else {
    f_values[i] <- NA
  }
}

f_df <- bind_rows(f_list)

# Define the path for the output file
output_file_path <- file.path(outdir, "f_stats_bootstrap.csv")
# Write the result tibble to a CSV file
write.csv(f_df, output_file_path, row.names = FALSE)

# === Summarize and plot results ===
f_clean <- f_values[!is.na(f_values)]
f_mean <- mean(f_clean)
df1 <- length(movie_levels) - 1
df2 <- (n_pairs - 1) * df1
f_crit <- qf(1 - alpha, df1 = df1, df2 = df2)

prop_above <- mean(f_clean > f_crit)

# Re-run ANOVA with original N = 56 pairs
original_pairs <- final_tibble %>%
  filter(Pair_Type == "Real") %>%
  distinct(Pair, Subject1, Subject2)

# Prepare data for ANOVA
original_anova_data <- final_tibble %>%
  filter(Pair %in% original_pairs$Pair) %>%
  group_by(Pair, Movie) %>%
  summarise(ISC = mean(FisherZ), .groups = "drop") %>%
  mutate(
    Movie = factor(Movie),
    Pair = factor(Pair)
  )

# Run repeated-measures ANOVA
original_result <- ezANOVA(
  data = original_anova_data,
  dv = ISC,
  wid = Pair,
  within = Movie,
  type = 3,
  detailed = TRUE
)

# Extract stats
original_stats <- original_result$ANOVA %>% filter(Effect == "Movie")
original_F <- original_stats$F
original_p <- original_stats$p
original_ges <- original_stats$ges

# === Create summary tibble ===
summary_stats <- tibble(
  Original_F = original_F,
  Original_p = original_p,
  Original_ges = original_ges,
  Mean_F = f_mean,
  Critical_F = f_crit,
  Proportion_Above_Critical = prop_above
)


# Define output path
summary_file_path <- file.path(outdir, "f_summary_stats.csv")

# Write to CSV
write.csv(summary_stats, summary_file_path, row.names = FALSE)

cat("Mean F:", round(f_mean, 3), "\n")
cat("Critical F (α = 0.05):", round(f_crit, 3), "\n")
cat("Proportion above F-critical:", round(prop_above * 100, 1), "%\n")

# Plotting ----------------------------------------------------------------
theme_CABB <- function(){
  theme_minimal() %+replace% 
    theme(
      #text elements
      plot.title = element_text(             
        size = 20,                #set font size
        hjust = 0.5),             #title centered
      plot.subtitle = element_text(          #subtitle
        size = 24,                 #font size
        hjust = 0.5),            #subtitle centered
      axis.title = element_text(             #axis titles
        size = 18),               #font size
      axis.text = element_text(              #axis text
        size = 14),
      strip.text = element_text(
        size = 16))}                #font size

# === Empirical density ===
empirical_density <- density(f_clean)
f_empirical <- data.frame(
  F = empirical_density$x,
  density = empirical_density$y
)

# === Theoretical F-distribution over full range ===
x_vals <- seq(0, max(f_clean) + 1, length.out = 500)
f_theoretical <- data.frame(
  F = x_vals,
  density = df(x_vals, df1 = df1, df2 = df2)
)

# === Scale theoretical to match empirical peak ===
scale_factor <- max(f_empirical$density) / max(f_theoretical$density)
f_theoretical <- f_theoretical %>%
  mutate(density_scaled = density * scale_factor)

# === Final plot ===
plot_densities <- ggplot() +
  # Fill empirical density
  geom_area(data = f_empirical, aes(x = F, y = density),
            fill = "darkblue", alpha = 0.4) +
  # geom_line(data = f_empirical, aes(x = F, y = density),
  #           color = "darkblue", linewidth = 1.2, linetype = "dotted") +
  
  # Fill theoretical density
  geom_area(data = f_theoretical, aes(x = F, y = density_scaled),
            fill = "darkgray", alpha = 0.3) +
  # geom_line(data = f_theoretical, aes(x = F, y = density_scaled),
  #           color = "darkgray", linewidth = 1, linetype = "dotted") +
  
  # Vertical lines
  geom_vline(xintercept = f_crit, color = "red", linetype = "dashed", linewidth = 1) +
  geom_vline(xintercept = original_F, color = "darkgreen", linetype = "dashed", linewidth = 1) +
  geom_vline(xintercept = f_mean, color = "blue", linetype = "solid", linewidth = 1) +
  
  # Labels and theme
  labs(
    x = expression(italic(F)*"-statistic"),
    y = "Density"
  ) +
  theme_CABB()

# Print
plot_densities
# Save the plot
ggsave(filename = file.path(outdir_vis, "Theoretical_Empirical.png"), plot = plot_densities,
       dpi = 400, height = 6, width = 9, bg = "white")

