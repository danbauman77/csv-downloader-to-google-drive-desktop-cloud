# CSV Downloader To Google Drive (Desktop → Cloud)

Downloads a web-hosted csv file (unreachable via Google Sheets Formulas) to a Google Drive (Desktop Application) folder. Incorporates IFTTT or a similar service.

## Install

Download and install Google Drive for Desktop
https://ipv4.google.com/intl/en_zm/drive/download/

## Configure download.sh

###Edit FILE_URL of `download.sh`:

```bash

FILE_URL="https://www.aphis.usda.gov/sites/default/files/awa-hpa-actions.csv"

```

###Edit TARGET_DIR of `download.sh`:

```bash

TARGET_DIR="/Users/XXXX/My Drive/IFTTT/aphis_usda_gov_actions/csv"

```

Refer to this Google Sheet for Formulas and setup to create a monitor. 
https://docs.google.com/spreadsheets/d/1JKNtWSY2JzCdhbPLGF2WIhuzs-zxiHHoK1vRu5XziWg/edit?usp=sharing

#### Render in C2 of 'IFTTT' Google Sheet 


```

=IFERROR(QUERY(FILTER(importXML!A2:H, NOT(COUNTIF(base!H:H, importXML!H2:H)), importXML!H2:H<>""), "SELECT * LIMIT 1"), "")

```

#### Render in B2 of 'IFTTT' Google Sheet (Use IFTTT 'Google Sheets' Applet; Trigger on Change of Cell)
 
```

=IFERROR(IF(C2="", "", ARRAYFORMULA(TEXTJOIN("|||", TRUE, C2:J2))), "")

```

#### Render in A1 of 'importXML' Google Sheet

```

=IFERROR(if(timevalue(time(0,0,1))<timevalue(now())=TRUE, if(timevalue(now())<timevalue(time(23,58,59))=TRUE, QUERY(IMPORTDATA("https://drive.google.com/uc?export=download&id=FILE-ID-OF-CSV-FILE-DOWNLOADED-TO-GOOGLE-DRIVE-DESKTOP-UPLOADED-GOOGLE-DRIVE-CLOUD"), "select Col1, Col2, Col3, Col4, Col5, Col6, Col7 order by Col6 desc label Col1 'HTML', Col2 'DBA', Col3 'Certificate #', Col4 'Customer #', Col5 'License Category', Col6 'Date', Col7 'Enforcement Type'"), ""), ""), "")


```

#### Render at the end of the baseline table in Column A of 'base' Google Sheet

```

=ARRAYFORMULA(IFTTT!$A$4:$J)

```

