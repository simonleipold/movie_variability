
# Summary -----------------------------------------------------------------

# Run a parcel-wise ANOVA to detect differences in ISC between movies

# Packages ----------------------------------------------------------------


library(tidyverse)
library(ggplot2)
library(ggpubr)
library(broom)
library(rstatix)

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

# Filter rows where Pair_Type is "Real"
filtered_tibble <- combined_tibble %>%
  filter(Pair_Type == "Real")

# Create a new column 'Pair' combining 'Subject1' and 'Subject2'
final_tibble <- filtered_tibble %>%
  mutate(Pair = paste(Subject1, Subject2, sep = "_")) %>%
  mutate(Pair = as.factor(Pair)) %>% 
  mutate(Movie = as.factor(Movie)) %>% 
  mutate(Parcel = as.factor(Parcel))

# Perform within-subject ANOVA for each Parcel
results <- final_tibble %>%
  group_by(Parcel) %>%
  # Carry out the ANOVA with the anova_test function from rstatix
  anova_test(data = .,
                     dv = Correlation,
                     wid = Pair,
                     within = Movie)

# Initialize a list to store the results
extracted_data <- list()

# Loop through each element in the results$anova
for (i in seq_along(results$anova)) {
  # Extract F and p values using the specified paths
  F_value <- results$anova[[i]]$ANOVA$F
  p_value <- results$anova[[i]]$ANOVA$p
  parcel_number <- i
  
  # Store these values in the list
  extracted_data[[i]] <- list(Parcel = parcel_number, Fval = F_value, p = p_value)
}

# Convert the list of lists into a tibble
results_tibble <- dplyr::bind_rows(extracted_data)

# Apply Bonferroni correction for the p-values
results_tibble <- results_tibble %>%
  mutate(pfwe = p.adjust(p, method = "bonferroni", n = length(extracted_data)))

# join labels
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
    TRUE ~ as.character(Yeo_7network)  # This line handles any unexpected values
  ))

# Define the path for the output file
output_file_path <- file.path(outdir, "isc_anova.csv")

# Write the result tibble to a CSV file
write.csv(results_tibble, output_file_path, row.names = FALSE)

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

# get parcels with most and least variability
high <- 76
low <- 111

plot_tibble <- final_tibble %>% 
  rename(ISC = Correlation) %>% 
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
                         labels = c("Superior Temporal Gyrus",
                                    "Parahippocampal Gyrus")))

# plot mean and se
plot_se <- ggplot(stats_summary, aes(x = MovieInt, y = Avg, fill = Movie)) +
  geom_col() +  # Add colored bars for each movie
  geom_errorbar(aes(ymin = Avg - SE, ymax = Avg + SE), width = 0.2) +  # Add error bars for SE
  labs(x = "Movie",
       y = "ISC") +
  scale_fill_brewer(palette = "Dark2") +  # Apply a color palette for the bars
  facet_wrap(~ Parcel) +
  theme_CABB()+
  guides(fill = "none")
  
# Print the plot
plot_se
# Save the plot
ggsave(filename = file.path(outdir_vis, "ANOVA_ISC_example.png"), plot = plot_se,
      dpi = 400, height = 6, width = 9, bg = "white")

## Whole brain-plot
whole_plot_tibble <- final_tibble %>% group_by(Pair, Movie) %>% 
  summarize(ISC_avg = mean(Correlation))
# anova
library(ez)
ezANOVA(data = whole_plot_tibble, dv = ISC_avg, wid = Pair, within = Movie,
        type = 3)

# Calculate mean and standard error for each movie
stats_summary <- whole_plot_tibble %>%
  group_by(Movie) %>%
  summarise(
    Avg = mean(ISC_avg), 
    SE = sd(ISC_avg) / sqrt(n()),  # Calculate standard error
    .groups = 'drop'
  )
stats_summary$MovieInt <- as.factor(as.integer(stats_summary$Movie))

# plot mean and se
plot_whole_se <- ggplot(stats_summary, aes(x = MovieInt, y = Avg, fill = Movie)) +
  geom_col() +  # Add colored bars for each movie
  geom_errorbar(aes(ymin = Avg - SE, ymax = Avg + SE), width = 0.2) +  # Add error bars for SE
  labs(x = "Movie",
       y = "ISC") +
  scale_fill_brewer(palette = "Dark2") +  # Apply a color palette for the bars
  theme_CABB()+
  guides(fill = "none")

# Print the plot
plot_whole_se
# Save the plot
ggsave(filename = file.path(outdir_vis, "ANOVA_ISC_whole.png"), plot = plot_whole_se,
       dpi = 400, height = 6, width = 7, bg = "white")


# Variability/level correlation -------------------------------------------

# get average ISC per parcel and join with variability

corr_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  summarize(ISC = mean(Correlation))
corr_tibble$Parcel <- as.numeric(gsub("parcel", "", corr_tibble$Parcel))
corr_tibble <- corr_tibble %>%
  left_join(results_tibble, by = c("Parcel" = "Parcel")) %>% 
  select(-c(p, pfwe, Yeo_17network))
cor.test(corr_tibble$Fval, corr_tibble$ISC)

correlation_plot <- ggplot(corr_tibble, aes(x = Fval, y = ISC)) +
  geom_point(color = '#1f77b4', size = 2) +  # Scatter plot
  geom_smooth(method = 'lm', se = TRUE, color = '#ff7f0e') +  # Add a linear regression line
  theme_CABB() +  # Use a minimal theme for better appearance
  labs(x = expression(Variability~(italic(F))), 
       y = "ISC")
correlation_plot
ggsave(filename = file.path(outdir_vis, "ANOVA_F_ISC_correlation.png"), plot = correlation_plot,
       dpi = 400, height = 5, width = 5, bg = "white")
