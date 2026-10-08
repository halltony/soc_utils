# cleanse_bt4.R — Documentation

## Overview

`cleanse_bt4.R` reads bird observation records from an Excel workbook (`bt-4.xlsx`), applies a series of data cleansing rules to the `Records#1` sheet, writes the cleaned workbook to a new file retaining all original tabs, and prints a summary of the unique species remaining after cleansing.

---

## Requirements

### R packages

| Package | Purpose |
|---------|---------|
| `readxl` | Reading `.xlsx` files into R data frames |
| `dplyr` | Data manipulation (filtering, mutating) |
| `openxlsx` | Writing multi-sheet `.xlsx` output |

Install any missing packages with:

```r
install.packages(c("readxl", "dplyr", "openxlsx"))
```

---

## Input

| Property | Value |
|----------|-------|
| File | `bt-4.xlsx` |
| Sheet cleansed | `Records#1` |
| All other sheets | Read and passed through unchanged |

The file must be present in the R working directory. To change the path, update the `input_file` variable at the top of the script.

---

## Output

| Property | Value |
|----------|-------|
| File | `bt-4-clean.xlsx` |
| Sheet cleansed | `Records#1` (replaced with cleansed data) |
| All other sheets | Preserved with original names and data |

The output file is written to the working directory. All tab names from the original workbook are retained and appear in their original order.

> **Note:** Cell formatting and formulas in sheets other than `Records#1` are not preserved — only the data values are carried through.

---

## Cleansing Rules

All rules are applied to the `Species` column of the `Records#1` sheet.

### Row removal rules

The following rules remove entire rows from the dataset.

| # | Rule | Example removed |
|---|------|----------------|
| 1 | Rows where `Species` begins with `"Unidentified"` | `Unidentified duck` |
| 2 | Rows where `Species` contains `"/"` | `Tufted Duck/Scaup` |
| 3 | Rows where `Species` contains `" x "` (space-x-space) | `Mallard x Pintail` |
| 4 | Rows where `Species` begins with `"Domestic"` | `Domestic Goose` |

### Value transformation rules

The following rules modify values in place rather than removing rows.

| # | Rule | Example before | Example after |
|---|------|---------------|--------------|
| 5 | Trailing parenthesised text is stripped and any resulting whitespace is trimmed | `Redpoll (Lesser - cabaret)` | `Redpoll` |

The regex used for rule 5 is `\\s*\\([^)]+\\)\\s*$`, which matches an optional leading space, an opening parenthesis, any content that is not a closing parenthesis (including spaces, hyphens, and multiple words), a closing parenthesis, any trailing spaces, and the end of the string.

---

## Console Output

When run, the script prints the following to the console:

```
Rows before cleansing: <n>
Rows after cleansing:  <n>
Rows removed:          <n>
Clean data written to: bt-4-clean.xlsx

Unique species remaining: <n>

          Species Records
   Barn Owl             3
   Barn Swallow        12
   ...
```

The species summary is sorted alphabetically by species name and shows the number of records (rows) for each species after cleansing.

---

## Usage

Set your working directory to the folder containing `bt-4.xlsx`, then source the script:

```r
setwd("/path/to/your/data")
source("cleanse_bt4.R")
```

Or run it from the command line:

```bash
Rscript cleanse_bt4.R
```
