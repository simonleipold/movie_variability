# ------------------------------------------------------------
# Extract mean framewise displacement per movie and run ezANOVA
# ------------------------------------------------------------

library(tidyverse)
library(ez)

# -----------------------------
# Paths
# -----------------------------

fmriprep_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/BIDS_movie/derivatives/fmriprep"
subjectlist_file <- "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/subjectlist.csv"
timing_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/Logfiles/Movies/reformatted"

out_dir <- "/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/MovVar_ImagNeuro_Revision01/control_motion"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

TR <- 1

# -----------------------------
# Helper functions
# -----------------------------

format_pid <- function(x) {
  x <- as.character(x)
  x <- str_replace(x, "^sub-", "")
  x <- str_extract(x, "\\d+")
  sprintf("%03d", as.integer(x))
}

extract_fd_for_subject <- function(pid) {
  
  sub_id <- paste0("sub-", pid)
  
  confound_file <- file.path(
    fmriprep_dir,
    sub_id,
    "ses-mri01",
    "func",
    paste0(sub_id, "_ses-mri01_task-movies_run-1_desc-confounds_timeseries.tsv")
  )
  
  timing_file <- file.path(
    timing_dir,
    paste0(pid, "_timing.csv")
  )
  
  if (!file.exists(confound_file)) {
    warning("Missing confound file: ", confound_file)
    return(tibble())
  }
  
  if (!file.exists(timing_file)) {
    warning("Missing timing file: ", timing_file)
    return(tibble())
  }
  
  confounds <- read_tsv(
    confound_file,
    na = c("", "NA", "NaN", "n/a"),
    col_types = cols(
      .default = col_skip(),
      framewise_displacement = col_double()
    ),
    show_col_types = FALSE
  )
  
  timing <- read_csv(timing_file, show_col_types = FALSE) %>%
    mutate(
      Movie = factor(trialNr),
      start_row = floor(Onset / TR) + 1,
      end_row = ceiling(Offset / TR)
    )
  
  map_dfr(seq_len(nrow(timing)), function(i) {
    
    this_timing <- timing[i, ]
    
    fd_segment <- confounds$framewise_displacement[
      this_timing$start_row:this_timing$end_row
    ]
    
    tibble(
      PID = sub_id,
      Movie = this_timing$Movie,
      framewise_displacement = mean(fd_segment, na.rm = TRUE),
      n_volumes = length(fd_segment)
    )
  })
}

# -----------------------------
# Load subjects
# -----------------------------

subjects <- read_csv(subjectlist_file, show_col_types = FALSE) %>%
  mutate(PID = format_pid(PID)) %>%
  distinct(PID)

# -----------------------------
# Extract mean FD per subject and movie
# -----------------------------

whole_plot_tibble <- map_dfr(
  subjects$PID,
  extract_fd_for_subject
) %>%
  mutate(
    PID = factor(PID),
    Movie = factor(Movie)
  )

write_csv(
  whole_plot_tibble,
  file.path(out_dir, "framewise_displacement_by_subject_movie.csv")
)

# -----------------------------
# Descriptive statistics
# -----------------------------

fd_summary_by_movie <- whole_plot_tibble %>%
  group_by(Movie) %>%
  summarise(
    n = sum(!is.na(framewise_displacement)),
    mean_fd = round(mean(framewise_displacement, na.rm = TRUE), 3),
    sd_fd = round(sd(framewise_displacement, na.rm = TRUE), 3),
    .groups = "drop"
  )

write_csv(
  fd_summary_by_movie,
  file.path(out_dir, "framewise_displacement_summary_by_movie.csv")
)

# -----------------------------
# Repeated-measures ANOVA
# -----------------------------

anova_fd <- ezANOVA(
  data = whole_plot_tibble,
  dv = framewise_displacement,
  wid = PID,
  within = Movie,
  type = 3
)

anova_fd

write_csv(
  as_tibble(anova_fd$ANOVA),
  file.path(out_dir, "framewise_displacement_ezANOVA.csv")
)

# -----------------------------
# Visualization
# -----------------------------

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

p <- ggplot(whole_plot_tibble, aes(x = Movie, y = framewise_displacement)) +
  geom_boxplot(outlier.shape = NA) +
  geom_point(
    alpha = 0.25,
    position = position_jitter(width = 0.10, height = 0)
  ) +
  stat_summary(
    fun = mean,
    geom = "point",
    size = 2.5,
    color = "red"
  ) +
  theme_CABB() +
  labs(
    x = "Movie",
    y = "Mean framewise displacement"
  )

ggsave(
  filename = file.path(out_dir, "framewise_displacement_by_movie.png"),
  plot = p,
  width = 7,
  height = 5,
  dpi = 300
)
