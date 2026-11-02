library(readxl)
library(dplyr)
library(readr)
library(stringr)

# ---- Settings ----
csv_file    <- "clyde_list.csv"
avi_file    <- "AviList-v2026-20Oct2026-extended-version.xlsx"
avi_sheet   <- "AviList v2026"
output_file <- "clyde_list_with_avi.csv"

avi_seq_col <- "#"               # exact header of the taxon sequence column

# Regexes matched against normalised headers (lowercase, punctuation -> spaces)
pat_sci_csv <- "scientific"
pat_sci_avi <- "scientific"
pat_rank    <- "^rank$"

# ---- Helpers ----
norm_hdr  <- function(x) str_to_lower(str_squish(str_replace_all(x, "[^A-Za-z0-9]+", " ")))
norm_name <- function(x) str_to_lower(str_squish(x))

find_col <- function(df, pattern, label) {
  hdrs <- names(df)
  hits <- hdrs[str_detect(norm_hdr(hdrs), regex(pattern, ignore_case = TRUE))]
  if (length(hits) == 0)
    stop("No column matches '", pattern, "' for ", label,
         ". Available columns:\n  ", paste(hdrs, collapse = "\n  "))
  if (length(hits) > 1)
    warning("Multiple matches for ", label, ": ",
            paste(hits, collapse = ", "), " - using '", hits[1], "'.")
  hits[1]
}

# ---- Read (everything as text to avoid type surprises) ----
species <- read_csv(csv_file, col_types = cols(.default = col_character()))
avi     <- read_excel(avi_file, sheet = avi_sheet, col_types = "text")

csv_sci <- find_col(species, pat_sci_csv, "CSV: scientific name")
av_sci  <- find_col(avi,     pat_sci_avi, "AVI sheet: scientific name")
av_rank <- find_col(avi,     pat_rank,    "AVI sheet: rank")

if (!avi_seq_col %in% names(avi))
  stop("Column '", avi_seq_col, "' not found in AVI sheet. Available columns:\n  ",
       paste(names(avi), collapse = "\n  "))
av_seq <- avi_seq_col

# ---- Build lookup: species-rank rows only, one row per scientific name ----
lookup <- avi |>
  filter(norm_name(.data[[av_rank]]) == "species") |>
  transmute(key = norm_name(.data[[av_sci]]),
            avi_taxon_seq = suppressWarnings(as.numeric(.data[[av_seq]]))) |>
  filter(!is.na(key), key != "", !is.na(avi_taxon_seq))

dupes <- lookup |> count(key) |> filter(n > 1)
if (nrow(dupes) > 0)
  warning("Duplicate scientific names in AVI species rows (first kept): ",
          paste(dupes$key, collapse = ", "))
lookup <- distinct(lookup, key, .keep_all = TRUE)

# ---- Join onto the original CSV ----
out <- species |>
  mutate(.key = norm_name(.data[[csv_sci]])) |>
  left_join(lookup, by = c(".key" = "key")) |>
  select(-.key) |>
  rename(avi_list_taxon_seq = avi_taxon_seq)

# ---- Report unmatched names ----
unmatched <- out |> filter(is.na(avi_list_taxon_seq))
if (nrow(unmatched) > 0)
  warning(nrow(unmatched), " rows had no AVI species match:\n  ",
          paste(unmatched[[csv_sci]], collapse = "\n  "))

write_csv(out, output_file, na = "")
message("Wrote ", nrow(out), " rows to ", output_file,
        " (", sum(!is.na(out$avi_list_taxon_seq)), " matched)")