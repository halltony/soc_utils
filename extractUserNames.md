# Script Summary: User Name Extraction and Word Output

## Overview
This script extracts user names from an Excel spreadsheet, applies extensive data cleansing and normalization, and outputs a clean, sorted list of unique personal names to a Microsoft Word document formatted for efficient display.

---

## 1. Data Input
- Reads the Excel file **`Combined_BirdTrack_and_eBird.xlsx`**
- Uses the worksheet **`Records#1`**
- Extracts names from two columns:
  - `User name`
  - `Observer name`

---

## 2. Name Consolidation
- Combines all values from both columns into a single list
- Removes empty or missing values

---

## 3. Data Cleansing Rules
The following entries are removed or corrected:

### Removed entries
- Text contained in brackets (e.g. `John Smith (RSPB)`)
- Honorifics and titles:
  - `Mr`, `Mrs`, `Miss`, `Ms`, `Dr`, `Prof`, `Professor`
- Any name containing **“Anonymous”** (case-insensitive)
- Known non-person values (case-insensitive):
  - `(No UserName)`
  - `BirdGuides`
  - `BirdGuides-Details`
  - `eBird`
  - `Rare Bird Alert`
  - `Alba Ecology`
  - `Rspb Glasgow Local Group`
- Names consisting only of initials (e.g. `J S`, `A.B.`)
- Names containing only a single word (forename or surname only)

---

## 4. Name Normalisation
- Converts names written entirely in capital letters to proper case
- Capitalises forenames or surnames beginning in lower case
- Trims excess whitespace
- Ensures consistent formatting (e.g. `john SMITH` → `John Smith`)

---

## 5. De-duplication and Sorting
- Removes duplicate names across both source columns
- Sorts names alphabetically by **surname**, then **forename**

---

## 6. Summary Output
- Prints the total number of unique, cleaned names to the R console

Example:Total unique cleaned names: 742

---

## 7. Word Document Output
- Outputs **`Unique_User_Names.docx`**
- Page layout:
  - A4, portrait orientation
  - Moderate margins (1.91 cm left and right)
- Text formatting:
  - Arial
  - 12-point font

---

## 8. Table Layout
- Names are arranged into **three columns**
- Entries flow **left-to-right across each row**
- Layout maximises the number of names displayed per page
- Uses tab-separated formatting instead of tables to ensure:
  - No truncation
  - No layout errors
  - Reliable output even with very small datasets

---

## Summary
The script produces a clean, deduplicated, and alphabetically sorted list of personal names from BirdTrack and eBird data, formatted into a publication-ready Word document optimised for clarity and space efficiency.
