# reformatRSPB.py

Converts an RSPB bird sighting export (Excel) into two BirdTrack-ready upload files: one for **ARM** (Annual Reserve Monitoring / Species Records) rows and one for all other (**incidental**) records.

## What it does

For each row in the input file, the script:

1. **Calculates a count value**, using different rules for ARM vs. incidental records (e.g. converting `Estimate` to a `c`-prefixed value, `Minimum count` to a `+`-suffixed value, or `Y` presence flags to a numeric count).
2. **Derives the record date**:
   - ARM records use a fixed date for the year supplied on the command line — 15 April for resident species, 1 June for migrant species (species lists are hardcoded in the script).
   - Incidental records use the sighting's own `Start Date`.
3. **Builds a place name** from the dataset name plus feature/location (or feature type, for ARM records).
4. **Builds a comment string** by combining count units/status, primary count comments, activity, chick/egg/fledgling counts, and associated-count fields into a single semicolon-separated comment.
5. **Normalises the observer** — visitors, unknown observers, and RSPB staff are all recorded simply as `RSPB`.
6. **Flags sensitive records** (`RESTRICTED` or `SENSITIVE` sensitivity) with `Y`.
7. **Sets age/sex/plumage** JSON for records identified as Adult Male / Adult Female counts.
8. **Derives breeding evidence and activity codes** from BirdTrack-style codes, based on chick/fledgling counts, primary count unit (ARM), or recorded activity (incidental).
9. **Deduplicates** rows that share the same species, place, date, and observer by appending the RSPB Observation ID to the place name, then reports any duplicates that remain.
10. **Writes two Excel workbooks**: `ARM_<output_file_path>` and `Non_ARM_<output_file_path>`, each with columns:
    `Species, Count, Place, Latitude, Longitude, Date, Breeding evidence, Comment, Observer, Sensitive, Activity, Age and plumage, Source`.

## Requirements

- Python 3.10+ (uses `match`/`case`)
- `pandas`
- `xlsxwriter`
- `OSGridConverter`

Install dependencies:

```bash
pip install pandas xlsxwriter OSGridConverter
```

## Usage

```bash
python reformatRSPB.py -i <input_file.xlsx> -o <output_file.xlsx> -y <year>
```

| Argument | Description |
|---|---|
| `-i`, `--input_file_path` | Path to the RSPB Excel export (must contain a sheet named `Export`) |
| `-o`, `--output_file_path` | Base filename for the output; `ARM_` and `Non_ARM_` prefixes are added automatically |
| `-y`, `--year` | Year used to construct fixed dates for ARM records (residents: 15 April; migrants: 1 June) |

**Example:**

```bash
python reformatRSPB.py -i RSPB_Export_2024.xlsx -o BirdTrack_Upload.xlsx -y 2024
```

This produces `ARM_BirdTrack_Upload.xlsx` and `Non_ARM_BirdTrack_Upload.xlsx`.

## Input expectations

The input workbook must have a sheet called `Export` containing (among others) these columns:
`Observation ID`, `Dataset`, `Common Name`, `Primary Count`, `Primary Count Type`, `Primary Count Unit`, `Primary Count Comment`, `Status`, `Comments`, `Activity`, `Feature`, `Feature Types`, `Location`, `Latitude`, `Longitude`, `Start Date`, `Observer`, `Sensitivity`, `Eggs Min/Max`, `Chicks Min/Max/Present`, `Fledged Min/Max/Present`, `AssCount Count Unit`, `AssCount Count Value`, `AssCount Breeding Status Code`, `AssCount Activity Type Code`.

Rows are treated as **ARM** records if `'ARM Species Records'` appears in the `Dataset` field; all other rows are treated as incidental.

## Known limitations

- The resident/migrant species lists are hardcoded — any ARM species not in either list triggers an error message and no date is set for that row.
- `AssCount Comment` handling is currently commented out (per a note in the script, this field appears to have been removed from the source Export for 2023 onward).
- The `Age and plumage` field is only populated for `Adult Male` / `Adult Female` primary count units.
- Deduplication only makes place names unique for exact species/place/date/observer matches — it does not merge or sum counts.
