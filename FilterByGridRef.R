# ---------------------------------------------------------------
# Filter Lat/Long records from one or more Excel sheets by
# British National Grid ref and write matching records to a CSV
# ---------------------------------------------------------------
library(readxl)
library(sf)
library(dplyr)
library(purrr)
library(readr)

# ---- 1. Settings (edit these) ----------------------------------
infile    <- 'All birdtrack records to 20261010.xlsx'
sheets    <- c("Records#1", "Records#2")   # names, numbers (e.g. c(1, 3)), or NULL for all sheets
lat_col   <- "Lat"              # must be the same in every sheet
lon_col   <- "Long"
digits    <- 2                       # 1 = 10 km (NS66), 2 = 1 km (NS6065), 3 = 100 m ...
keep_refs <- c("NS5656", "NS5756", "NS5655", "NS5755")               # one or more grid refs to keep
outfile   <- "filtered.csv"
one_file_per_sheet <- FALSE          # TRUE = write a separate CSV for each sheet

# ---- 2. Work out which sheets to read --------------------------
all_sheets <- excel_sheets(infile)

if (is.null(sheets)) {
  sheets <- all_sheets
} else if (is.numeric(sheets)) {
  sheets <- all_sheets[sheets]
}

missing_sheets <- setdiff(sheets, all_sheets)
if (length(missing_sheets) > 0) {
  stop("Sheet(s) not found in workbook: ", paste(missing_sheets, collapse = ", "),
       "\nAvailable sheets: ", paste(all_sheets, collapse = ", "))
}

# ---- 3. Easting/Northing -> grid reference ---------------------
en_to_gridref <- function(e, n, digits = 1) {
  alphabet <- "ABCDEFGHJKLMNOPQRSTUVWXYZ"          # no letter I
  
  e100 <- floor(e / 100000)
  n100 <- floor(n / 100000)
  
  l1 <- (19 - n100) - (19 - n100) %% 5 + floor((e100 + 10) / 5)
  l2 <- ((19 - n100) * 5) %% 25 + e100 %% 5
  
  letters2 <- paste0(substr(alphabet, l1 + 1, l1 + 1),
                     substr(alphabet, l2 + 1, l2 + 1))
  
  div   <- 10^(5 - digits)
  e_num <- floor((e %% 100000) / div)
  n_num <- floor((n %% 100000) / div)
  
  paste0(letters2,
         formatC(e_num, width = digits, flag = "0", format = "d"),
         formatC(n_num, width = digits, flag = "0", format = "d"))
}

# ---- 4. Process one sheet --------------------------------------
process_sheet <- function(sheet_name) {
  df <- read_excel(infile, sheet = sheet_name)
  
  if (!all(c(lat_col, lon_col) %in% names(df))) {
    warning("Sheet '", sheet_name, "' skipped: column(s) '", lat_col,
            "' / '", lon_col, "' not found.")
    return(NULL)
  }
  
  df[[lat_col]] <- suppressWarnings(as.numeric(df[[lat_col]]))
  df[[lon_col]] <- suppressWarnings(as.numeric(df[[lon_col]]))
  
  # Make all other columns character so sheets with differing
  # column types can be combined without errors
  df <- df |>
    mutate(across(-all_of(c(lat_col, lon_col)), as.character))
  
  bad <- is.na(df[[lat_col]]) | is.na(df[[lon_col]])
  if (any(bad)) {
    message("Sheet '", sheet_name, "': ", sum(bad),
            " row(s) with missing coordinates excluded.")
  }
  df_ok <- df[!bad, ]
  if (nrow(df_ok) == 0) return(NULL)
  
  # Lat/Long (WGS84) -> OSGB36 Easting/Northing
  pts <- st_as_sf(df_ok, coords = c(lon_col, lat_col), crs = 4326, remove = FALSE) |>
    st_transform(27700)
  xy <- st_coordinates(pts)
  
  df_ok$Easting  <- xy[, "X"]
  df_ok$Northing <- xy[, "Y"]
  df_ok$GridRef  <- en_to_gridref(df_ok$Easting, df_ok$Northing, digits)
  df_ok$Sheet    <- sheet_name
  
  total <- nrow(df_ok)
  out <- df_ok |> filter(toupper(GridRef) %in% toupper(keep_refs))
  message("Sheet '", sheet_name, "': ", nrow(out), " of ", total, " records matched.")
  out
}

# ---- 5. Run across all selected sheets -------------------------
results <- set_names(sheets) |> map(process_sheet)
results <- compact(results)      # drop skipped/empty sheets

if (length(results) == 0) stop("No records found in any sheet.")

# ---- 6. Write to CSV --------------------------------------------
if (one_file_per_sheet) {
  iwalk(results, function(d, nm) {
    f <- paste0(tools::file_path_sans_ext(outfile), "_",
                gsub("[^A-Za-z0-9_-]", "_", nm), ".csv")
    write_csv(d, f)
    message("Written ", nrow(d), " records to ", normalizePath(f))
  })
} else {
  combined <- bind_rows(results) |>
    relocate(Sheet, GridRef, .after = last_col())
  write_csv(combined, outfile)
  message("Written ", nrow(combined), " records to ", normalizePath(outfile))
}