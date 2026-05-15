# Summary -----------------------------------------------------------------

# Run parcel-wise ANOVAs to detect differences in ISC between movies
# Schaefer 2018 atlas: 300 parcels, 17 networks


# Packages ----------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(rstatix)
library(ez)


# Prelude -----------------------------------------------------------------

project_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie"

main_out_dir <- file.path(
  project_dir,
  "Scripts",
  "MovVar_ImagNeuro_Revision01",
  "CABB_Schaefer"
)

indir <- file.path(main_out_dir, "dataframes")

outdir <- file.path(main_out_dir, "r_output_anova")
if (!dir.exists(outdir)) {
  dir.create(outdir, recursive = TRUE)
}

outdir_vis <- file.path(main_out_dir, "visualizations")
if (!dir.exists(outdir_vis)) {
  dir.create(outdir_vis, recursive = TRUE)
}

movies <- paste0("movie", 1:8)
parcels <- paste0("parcel", 1:300)

labels <- read_tsv(
  file = file.path(
    project_dir,
    "MRI",
    "Schaefer_atlas",
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_labels.tsv"
  ),
  show_col_types = FALSE
)


# Theme -------------------------------------------------------------------

theme_CABB <- function() {
  theme_minimal() %+replace%
    theme(
      plot.title = element_text(size = 20, hjust = 0.5),
      plot.subtitle = element_text(size = 24, hjust = 0.5),
      axis.title = element_text(size = 18),
      axis.text = element_text(size = 14),
      strip.text = element_text(size = 14)
    )
}


# Main --------------------------------------------------------------------

files_list <- expand.grid(movie = movies, parcel = parcels) %>%
  mutate(filename = paste0("ISCdf_upper_", movie, "_", parcel, ".csv")) %>%
  pmap(function(movie, parcel, filename) {
    
    file_path <- file.path(indir, filename)
    
    if (file.exists(file_path)) {
      read_csv(
        file_path,
        col_types = cols(
          Pair_Type = col_character(),
          Subject1 = col_character(),
          Subject2 = col_character(),
          Correlation = col_double()
        )
      ) %>%
        mutate(Movie = movie, Parcel = parcel)
    } else {
      warning(paste("File does not exist:", file_path))
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
    FisherZ = atanh(Correlation)
  )


# Parcel-wise ANOVA --------------------------------------------------------

results_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  anova_test(
    dv = FisherZ,
    wid = Pair,
    within = Movie
  ) %>%
  get_anova_table() %>%
  ungroup() %>%
  filter(Effect == "Movie") %>%
  mutate(
    Parcel = as.integer(str_remove(as.character(Parcel), "parcel")),
    Fval = F,
    pfwe = p.adjust(p, method = "bonferroni", n = 300)
  ) %>%
  select(Parcel, Fval, p, pfwe, ges)

results_tibble <- results_tibble %>%
  left_join(labels, by = c("Parcel" = "one_based")) %>%
  select(
    Parcel,
    label,
    Yeo_17_network,
    Fval,
    p,
    pfwe,
    ges
  )

write.csv(
  results_tibble,
  file.path(outdir, "isc_anova.csv"),
  row.names = FALSE
)


# Whole-brain ISC ANOVA and Figure 3A-style plot --------------------------

whole_plot_tibble <- final_tibble %>%
  group_by(Pair, Movie) %>%
  summarize(
    ISC_avg = mean(FisherZ),
    .groups = "drop"
  )

whole_anova <- ezANOVA(
  data = whole_plot_tibble,
  dv = ISC_avg,
  wid = Pair,
  within = Movie,
  type = 3
)

print(whole_anova)

capture.output(
  whole_anova,
  file = file.path(outdir, "whole_brain_isc_anova.txt")
)

stats_summary_whole <- whole_plot_tibble %>%
  group_by(Movie) %>%
  summarise(
    Avg = mean(ISC_avg),
    SE = sd(ISC_avg) / sqrt(n()),
    .groups = "drop"
  ) %>%
  mutate(MovieInt = factor(readr::parse_number(as.character(Movie)), levels = 1:8))

whole_plot_tibble <- whole_plot_tibble %>%
  mutate(MovieInt = factor(readr::parse_number(as.character(Movie)), levels = 1:8))

write.csv(
  whole_plot_tibble,
  file.path(outdir, "Figure3A.csv"),
  row.names = FALSE
)

plot_whole_se_dots <- ggplot(stats_summary_whole, aes(x = MovieInt, y = Avg, fill = Movie)) +
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
  labs(x = "Movie", y = "ISC") +
  scale_fill_brewer(palette = "Dark2") +
  theme_CABB() +
  guides(fill = "none")

plot_whole_se_dots

ggsave(
  filename = file.path(outdir_vis, "ANOVA_ISC_whole_dots.png"),
  plot = plot_whole_se_dots,
  dpi = 400,
  height = 6,
  width = 7,
  bg = "white"
)


# Variability/level correlation -------------------------------------------

corr_tibble <- final_tibble %>%
  group_by(Parcel) %>%
  summarize(
    ISC = mean(FisherZ),
    .groups = "drop"
  ) %>%
  mutate(Parcel = as.integer(str_remove(as.character(Parcel), "parcel"))) %>%
  left_join(results_tibble, by = "Parcel")

isc_variability_correlation <- cor.test(corr_tibble$Fval, corr_tibble$ISC)

print(isc_variability_correlation)

capture.output(
  isc_variability_correlation,
  file = file.path(outdir, "isc_variability_correlation.txt")
)

write.csv(
  corr_tibble,
  file.path(outdir, "Figure3D.csv"),
  row.names = FALSE
)

correlation_plot <- ggplot(corr_tibble, aes(x = Fval, y = ISC)) +
  geom_point(color = "#1f77b4", size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "#ff7f0e") +
  theme_CABB() +
  labs(
    x = expression(Variability~(italic(F))),
    y = "ISC"
  )

correlation_plot

ggsave(
  filename = file.path(outdir_vis, "ANOVA_F_ISC_correlation.png"),
  plot = correlation_plot,
  dpi = 400,
  height = 5,
  width = 5,
  bg = "white"
)
