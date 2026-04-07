# CSV Downloader To Google Sheets

Python script that downloads a web-hosted CSV file and pushes it to a Google Sheet via service account credentials. Designed for CSVs unreachable by Google Sheets' built-in IMPORTDATA (e.g., files behind redirects or non-standard headers).

## Install

1. Ensure Python 3.7+ and `curl` are installed (curl ships with macOS/Linux)
2. Install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup

### Google Service Account

1. Create a service account in Google Cloud Console
2. Enable the Google Sheets API
3. Download the credentials JSON file
4. Share the target Google Sheet with the service account email (Editor access)
5. Place `credentials.json` in the project directory (or set path in config)

### Configure

Edit `config.json`:

```json
{
  "csv_file_url": "https://www.aphis.usda.gov/sites/default/files/awa-hpa-actions.csv",
  "csv_filename": "awa-hpa-actions.csv",
  "csv_credentials_file": "credentials.json",
  "csv_spreadsheet_id": "your-spreadsheet-id-here",
  "csv_sheet_name": "importXML"
}
```

- `csv_spreadsheet_id`: the long ID from the Google Sheet URL (`https://docs.google.com/spreadsheets/d/THIS_PART/edit`)
- `csv_sheet_name`: the tab name to clear and overwrite

### Run

```bash
python download.py
```

The script will:
- Download the CSV via `curl` to a temp file (some government servers block Python's requests library; curl uses the system TLS stack and is not blocked)
- Parse it using the encoding specified in `csv_encoding` (default `cp1252` for this APHIS file)
- Clear the target sheet tab
- Write all rows to the sheet
- Delete the temp file
- Log results to `downloader.log`

### Schedule (cron)

To run automatically, add a crontab entry. Example -- every 4 hours:

```bash
crontab -e
```

```
0 */4 * * * cd /path/to/aphis-csv-to-google-sheets && ./venv/bin/python download.py >> downloader.log 2>&1
```

## Google Sheets Monitor Setup (IFTTT)

Refer to this Google Sheet for formulas and setup:
https://docs.google.com/spreadsheets/d/1JKNtWSY2JzCdhbPLGF2WIhuzs-zxiHHoK1vRu5XziWg/edit?usp=sharing

#### C2 of 'IFTTT' tab

```
=IFERROR(QUERY(FILTER(importXML!A2:H, NOT(COUNTIF(base!H:H, importXML!H2:H)), importXML!H2:H<>""), "SELECT * LIMIT 1"), "")
```

#### B2 of 'IFTTT' tab (trigger IFTTT 'Google Sheets' Applet on cell change)

```
=IFERROR(IF(C2="", "", ARRAYFORMULA(TEXTJOIN("|||", TRUE, C2:J2))), "")
```

#### A1 of 'importXML' tab

```
=IFERROR(if(timevalue(time(0,0,1))<timevalue(now())=TRUE, if(timevalue(now())<timevalue(time(23,58,59))=TRUE, QUERY(IMPORTDATA("https://drive.google.com/uc?export=download&id=FILE-ID"), "select Col1, Col2, Col3, Col4, Col5, Col6, Col7 order by Col6 desc label Col1 'HTML', Col2 'DBA', Col3 'Certificate #', Col4 'Customer #', Col5 'License Category', Col6 'Date', Col7 'Enforcement Type'"), ""), ""), "")
```

#### End of baseline table in Column A of 'base' tab

```
=ARRAYFORMULA(IFTTT!$A$4:$J)
```

### Acknowledgements
- Coded and debugged with the assistance of claude.ai
