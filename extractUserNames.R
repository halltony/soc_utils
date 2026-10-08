library(readxl)
library(dplyr)
library(stringr)
library(officer)
library(tibble)

# -----------------------
# Parameters
# -----------------------
input_file  <- "Combined_BirdTrack_and_eBird.xlsx"
sheet_name  <- "Records#1"
name_cols   <- c("User name", "Observer name")
output_file <- "Unique_User_Names.docx"
n_cols <- 3  # Number of columns in Word

# Values to exclude
exclude_values <- c(
  "(No UserName)",
  "BirdGuides",
  "BirdGuides-Details",
  "eBird",
  "Rare Bird Alert",
  "Alba Ecology",
  "Rspb Glasgow Local Group"
)

# Prefixes to remove
prefix_regex <- "^(mr|mrs|miss|ms|dr|prof|professor)\\.?\\s+"

# -----------------------
# Helper: normalize ALL CAPS words
# -----------------------
fix_all_caps_words <- function(x) {
  words <- str_split(x, "\\s+")[[1]]
  words <- sapply(words, function(w) {
    if (str_detect(w, "^[A-Z]{2,}$")) str_to_title(str_to_lower(w)) else w
  })
  paste(words, collapse = " ")
}

# -----------------------
# Read Excel
# -----------------------
df <- read_excel(input_file, sheet = sheet_name)

# Combine both name columns
all_names <- unlist(df[name_cols], use.names = FALSE)

# -----------------------
# Clean & normalize names
# -----------------------
users_clean <- tibble(name = all_names) %>%
  filter(!is.na(name)) %>%
  mutate(name = str_remove_all(name, "\\s*\\([^)]*\\)")) %>%   # remove brackets
  mutate(name = str_squish(name)) %>%                           # remove extra spaces
  filter(!tolower(name) %in% tolower(exclude_values)) %>%       # case-insensitive exclusion
  filter(!str_detect(name, regex("anonymous", ignore_case = TRUE))) %>%  # remove Anonymous
  mutate(name = str_remove(name, regex(prefix_regex, ignore_case = TRUE))) %>%
  mutate(name = if_else(str_detect(name, "^[A-Z\\s'.-]+$"),
                        str_to_lower(name),
                        name)) %>%
  mutate(clean_name = str_to_title(name)) %>%
  filter(!str_detect(clean_name, "^([A-Z]\\.?\\s*){1,3}$")) %>%    # remove initials only
  filter(str_count(clean_name, "\\S+") >= 2) %>%                   # must have at least 2 words
  mutate(surname = word(clean_name, -1)) %>%
  distinct(clean_name, surname) %>%
  arrange(surname, clean_name)

# -----------------------
# Report total
# -----------------------
cat("Total unique cleaned names:", nrow(users_clean), "\n")
names_out <- users_clean$clean_name

# -----------------------
# Split names into rows for n_cols
# -----------------------
n_rows <- ceiling(length(names_out) / n_cols)
rows <- split(names_out, ceiling(seq_along(names_out)/n_cols))

# Create a string per row, separated by tabs for columns
row_strings <- sapply(rows, function(x) paste(x, collapse = "\t"))

# -----------------------
# Create Word document
# -----------------------
doc <- read_docx() %>%
  body_set_default_section(
    prop_section(
      page_size = page_size(orient = "portrait"),
      page_margins = page_mar(
        top = 2.54, bottom = 2.54,
        left = 1.91, right = 1.91
      )
    )
  )

# Add each row to Word
for (r in row_strings) {
  doc <- body_add_par(doc, r, style = "Normal")
}

# Save
print(doc, target = output_file)