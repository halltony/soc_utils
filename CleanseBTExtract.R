library(readxl)
library(dplyr)
library(openxlsx)

# ── Load ──────────────────────────────────────────────────────────────────────
input_file  <- "bt-4.xlsx"
sheet_name  <- "Records#1"

records <- read_excel(input_file, sheet = sheet_name)

cat("Rows before cleansing:", nrow(records), "\n")

# ── Cleanse ───────────────────────────────────────────────────────────────────
records_clean <- records |>
  filter(!startsWith(Species, "Unidentified")) |>        # rule 1: remove Unidentified
  filter(!grepl("/", Species, fixed = TRUE)) |>          # rule 2: remove hybrids (/)
  filter(!grepl(" x ", Species, fixed = TRUE)) |>        # rule 3: remove hybrids ( x )
  filter(!startsWith(Species, "Domestic")) |>            # rule 4: remove Domestic
  mutate(Species = trimws(sub("\\s*\\([^)]+\\)\\s*$", "", Species)))  # rule 5: strip trailing (...)

cat("Rows after cleansing: ", nrow(records_clean), "\n")
cat("Rows removed:         ", nrow(records) - nrow(records_clean), "\n")

# ── Save (preserving all tabs) ────────────────────────────────────────────────
output_file <- "bt-4-clean.xlsx"

# Load all sheets from the original workbook
all_sheet_names <- excel_sheets(input_file)
all_sheets <- lapply(all_sheet_names, function(s) read_excel(input_file, sheet = s))
names(all_sheets) <- all_sheet_names

# Replace the target sheet with the cleaned data
all_sheets[[sheet_name]] <- records_clean

# Write all sheets to the output workbook
wb <- createWorkbook()
for (s in all_sheet_names) {
  addWorksheet(wb, s)
  writeData(wb, sheet = s, x = all_sheets[[s]])
}
saveWorkbook(wb, file = output_file, overwrite = TRUE)

cat("Clean data written to:", output_file, "\n")

# ── Species summary ───────────────────────────────────────────────────────────
species_summary <- records_clean |>
  count(Species, name = "Records") |>
  arrange(Species)

cat("\nUnique species remaining:", nrow(species_summary), "\n\n")
print(as.data.frame(species_summary), row.names = FALSE)