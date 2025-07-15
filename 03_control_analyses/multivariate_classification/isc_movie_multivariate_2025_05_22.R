
# Summary -----------------------------------------------------------------

# Run a multivariate classification to differentiate movies based on ISC values

# Packages ----------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(glmnet)
library(caret)

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
outdir = "r_output_class"
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

# Filter rows where Pair_Type is "Real"
combined_tibble <- combined_tibble %>%
  filter(Pair_Type == "Real")

# Create a new column 'Pair' combining 'Subject1' and 'Subject2'
final_tibble <- combined_tibble %>%
  mutate(Pair = paste(Subject1, Subject2, sep = "_")) %>%
  mutate(
    Pair = as.factor(Pair),
    Movie = as.factor(Movie),
    Parcel = as.factor(Parcel),
    FisherZ = 0.5 * log((1 + Correlation) / (1 - Correlation))
  )

# ======================
# Data Preparation

# Wide format: rows = Pair x Movie, columns = parcels
multivariate_df <- final_tibble %>%
  select(Pair, Movie, Parcel, FisherZ) %>%
  pivot_wider(names_from = Parcel, values_from = FisherZ)

# Feature matrix (X) and labels (y)
X <- multivariate_df %>% select(starts_with("parcel")) %>% as.matrix()
X <- scale(X) # Center & scale (standardization)
y <- as.factor(multivariate_df$Movie)

# ======================
# Model Training

train_control <- trainControl(
  method = "cv",
  number = 5,
  verboseIter = TRUE,
  savePredictions = "final"
)

set.seed(142)
model <- train(
  x = X, y = y,
  method = "glmnet",
  family = "multinomial",
  trControl = train_control,
  tuneLength = 5
)


# Print accuracy summary
print(model)

# ======================
# Confusion Matrix

# Filter best tuning combination
preds_cv <- model$pred %>%
  filter(lambda == model$bestTune$lambda, alpha == model$bestTune$alpha) %>%
  arrange(rowIndex)

# Get corresponding reference labels (assuming no subsetting)
y_cv <- factor(y[preds_cv$rowIndex], levels = levels(y))
preds_cv$pred <- factor(preds_cv$pred, levels = levels(y))

# Compute confusion matrix
conf_matrix_cv <- confusionMatrix(preds_cv$pred, y_cv)
print(conf_matrix_cv)

# === Save Classification Metrics ===
# Save raw confusion matrix and per-class metrics
write.csv(as.data.frame(conf_matrix_cv$table),
          file.path(outdir, "confusion_matrix_counts.csv"), row.names = FALSE)

write.csv(as.data.frame(conf_matrix_cv$byClass),
          file.path(outdir, "per_class_metrics.csv"), row.names = TRUE)

# Save overall stats
overall_stats <- as.data.frame(t(conf_matrix_cv$overall))
write.csv(overall_stats, file.path(outdir, "overall_classification_stats.csv"), 
          row.names = FALSE)

# ======================
# ggplot Confusion Matrix

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
        size = 10),
      strip.text = element_text(
        size = 16))}                #font size

# Rename factor levels for display
rename_movies <- function(x) {
  factor(x, levels = paste0("movie", 1:8),
         labels = paste0("Movie #", 1:8))
}

# Apply relabeling
cm_df <- as.data.frame(conf_matrix_cv$table) %>%
  group_by(Reference) %>%
  mutate(Prop = Freq / sum(Freq)) %>%
  ungroup() %>%
  mutate(
    Reference = rename_movies(Reference),
    Prediction = rename_movies(Prediction)
  )

# Create plot
cm_plot <- ggplot(cm_df, aes(x = Prediction, y = Reference, fill = Prop)) +
  geom_tile(color = "white") +
  geom_text(aes(label = sprintf("%.2f", Prop)), color = "black", size = 6) +
  scale_fill_gradient(low = "white", high = "#1f78b4") +
  labs(x = "\nPredicted Movie", y = "True Movie\n", fill = "Proportion") +
  guides(fill = "none")+  # Hide legend
  theme_CABB()

# Print the plot
cm_plot
# Save the plot
ggsave(filename = file.path(outdir_vis, "movie_confusion_matrix.png"),
       plot = cm_plot,
       dpi = 400, height = 7, width = 10, bg = "white")

# === Permutation Test ===
n_perms <- 1000
perm_accuracies <- numeric(n_perms)

for (i in 1:n_perms) {
  y_perm <- sample(y)  # Shuffle labels
  model_perm <- train(
    x = X, y = y_perm,
    method = "glmnet",
    family = "multinomial",
    trControl = trainControl(method = "cv", number = 5),
    tuneLength = 5
  )
  perm_accuracies[i] <- max(model_perm$results$Accuracy)
  # Print progress every 10 permutations
  if (i %% 10 == 0) {
    cat(sprintf("Completed permutation %d / %d\n", i, n_perms))
    flush.console()
  }
}

# Compute p-value
observed_accuracy <- max(model$results$Accuracy)
p_val <- (sum(perm_accuracies >= observed_accuracy) + 1) / (length(perm_accuracies) + 1)

# Print
cat(sprintf("Observed accuracy: %.3f | p = %.4f\n", observed_accuracy, p_val))

# === Save permutation distribution ===
perm_df <- tibble(PermutationAccuracy = perm_accuracies)
write_csv(perm_df, file.path(outdir, "permutation_accuracies.csv"))

# === Plot permutation distribution ===
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

perm_plot <- ggplot(perm_df, aes(x = PermutationAccuracy)) +
  geom_histogram(bins = 100, fill = "gray", color = "white", alpha = 0.7) +
  geom_vline(xintercept = observed_accuracy, color = "#1f78b4", linetype = "dashed", linewidth = 1) +
  geom_vline(xintercept = 1/8, color = "gray30", linetype = "solid", linewidth = 0.5) +
  labs(
    x = "Accuracy",
    y = "Frequency"
  ) +
  theme_CABB()

perm_plot

ggsave(filename = file.path(outdir_vis, "permutation_accuracy_null_distribution.png"),
       plot = perm_plot, dpi = 400, height = 6, width = 8, bg = "white")

