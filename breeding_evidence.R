# breeding_evidence.R
# Reads a BirdTrack breeding summary CSV and produces three output CSVs:
#   1. confirmed_breeding.csv  - species with confirmed breeding records
#   2. probable_breeding.csv   - additional species with probable (but no confirmed) records
#   3. possible_breeding.csv   - additional species with possible (but no probable/confirmed) records
#
# Input:  breedingSummary.csv  (must be in the working directory)
# Output: three CSVs written to the working directory

library(dplyr)
library(readr)

# ── 1. Load data ──────────────────────────────────────────────────────────────

input_file <- "breedingSummary.csv"

if (!file.exists(input_file)) {
  stop("Cannot find '", input_file, "' in the working directory: ", getwd())
}

df <- read_csv(input_file, show_col_types = FALSE)

# Validate required columns
required_cols <- c("Species", "Confirmed Records", "Probable Records", "Possible Records")
missing_cols  <- setdiff(required_cols, names(df))
if (length(missing_cols) > 0) {
  stop("Missing column(s) in input file: ", paste(missing_cols, collapse = ", "))
}

# Coerce count columns to numeric (in case they were read as character)
df <- df %>%
  mutate(
    `Confirmed Records` = as.integer(`Confirmed Records`),
    `Probable Records`  = as.integer(`Probable Records`),
    `Possible Records`  = as.integer(`Possible Records`)
  )

total_species <- nrow(df)
cat(sprintf("Loaded %d species from '%s'\n\n", total_species, input_file))

# ── 2. Classify species ───────────────────────────────────────────────────────

# Confirmed: at least one confirmed breeding record
confirmed <- df %>%
  filter(`Confirmed Records` > 0) %>%
  arrange(desc(`Confirmed Records`), Species) %>%
  select(Species, `Confirmed Records`)

# Probable: at least one probable record AND no confirmed records
probable <- df %>%
  filter(`Probable Records` > 0, `Confirmed Records` == 0) %>%
  arrange(desc(`Probable Records`), Species) %>%
  select(Species, `Probable Records`)

# Possible: at least one possible record AND no probable or confirmed records
possible <- df %>%
  filter(`Possible Records` > 0, `Probable Records` == 0, `Confirmed Records` == 0) %>%
  arrange(desc(`Possible Records`), Species) %>%
  select(Species, `Possible Records`)

# ── 3. Report to console ──────────────────────────────────────────────────────

cat("════════════════════════════════════════════════════════\n")
cat(sprintf("CONFIRMED BREEDING  (%d species)\n", nrow(confirmed)))
cat("════════════════════════════════════════════════════════\n")
print(confirmed, n = Inf)

cat("\n")
cat("────────────────────────────────────────────────────────\n")
cat(sprintf("PROBABLE BREEDING (no confirmed records)  (%d species)\n", nrow(probable)))
cat("────────────────────────────────────────────────────────\n")
print(probable, n = Inf)

cat("\n")
cat("────────────────────────────────────────────────────────\n")
cat(sprintf("POSSIBLE BREEDING (no probable/confirmed records)  (%d species)\n", nrow(possible)))
cat("────────────────────────────────────────────────────────\n")
print(possible, n = Inf)

cat("\n")
cat("════════════════════════════════════════════════════════\n")
cat(sprintf("SUMMARY\n"))
cat(sprintf("  Total species in file     : %d\n", total_species))
cat(sprintf("  Confirmed breeding        : %d\n", nrow(confirmed)))
cat(sprintf("  Probable only             : %d\n", nrow(probable)))
cat(sprintf("  Possible only             : %d\n", nrow(possible)))
cat(sprintf("  No breeding evidence      : %d\n",
            total_species - nrow(confirmed) - nrow(probable) - nrow(possible)))
cat("════════════════════════════════════════════════════════\n")

# ── 4. Save output CSVs ───────────────────────────────────────────────────────

write_csv(confirmed, "confirmed_breeding.csv")
write_csv(probable,  "probable_breeding.csv")
write_csv(possible,  "possible_breeding.csv")

cat("\nOutput files written:\n")
cat(sprintf("  confirmed_breeding.csv  (%d rows)\n", nrow(confirmed)))
cat(sprintf("  probable_breeding.csv   (%d rows)\n", nrow(probable)))
cat(sprintf("  possible_breeding.csv   (%d rows)\n", nrow(possible)))
