# CMPE 138 Traffic Safety Project

## What the Application Is

This application uses real traffic-safety data from the BigQuery public dataset:

`bigquery-public-data.dataflix_traffic_safety`

The dataset includes details on fatal crashes, road conditions, and vehicle types categorized by state, year, and roadway.

The project copies selected traffic-safety data into a BigQuery dataset named `cmpe138_project` for analysis.

## System Diagram

To come.

## What to Install

Install the Google Cloud BigQuery Python client:

```powershell
pip install google-cloud-bigquery
```

Install the Google Cloud CLI separately if it is not already installed.

## How to Sign In

Sign in with Google Application Default Credentials:

```powershell
gcloud auth application-default login
```

## How to Set the Project ID

Set the Google Cloud project:

```powershell
gcloud config set project YOUR_PROJECT_ID
```

For the current project:

```powershell
gcloud config set project cmpe138-fa26
```

Verify the active project:

```powershell
gcloud config get-value project
```

## How to Seed

The seed script copies selected FARS traffic-safety data into the
`cmpe138_project` dataset. By default, it loads data from 2010 through 2018 and caps each copy operation at 150,000,000 bytes billed. For Phase 2, we loaded data from 2000 through 2018 and raised the cap to 300,000,000 bytes per copy operation. The Phase 2 seed contained 4,725,767 rows in total.

The script loads seven related tables:

```text
accident
vehicle
person
distract
drimpair
factor
safetyeq
```

The source dataset is:

```text
bigquery-public-data.dataflix_traffic_safety
```

The destination dataset is:

```text
cmpe138-fa26.cmpe138_project
```

The seed selects only the columns needed by the project questions. It performs
dry-run byte estimates, applies the configured MAX_BYTES_BILLED limit to each table copy,
asks for confirmation before replacing the destination tables, declares
non-enforced primary and foreign keys, and prints duplicate-key counts.

Seed command:

```powershell
$env:GCP_PROJECT_ID = "cmpe138-fa26"
$env:FARS_START_YEAR = "2000"
$env:FARS_END_YEAR = "2018"
$env:MAX_BYTES_BILLED = "300000000"
python seed.py
```

Seed output:

```text
Copy all seven data tables and replace all tables? [y/N]: y

Adding non-enforced primary and foreign keys...
Seed completed.
Created table: cmpe138-fa26.cmpe138_project.accident
Accident row count: 664,739
Created table: cmpe138-fa26.cmpe138_project.vehicle
Vehicle row count: 1,002,749
Created table: cmpe138-fa26.cmpe138_project.person
Person row count: 1,686,304
Created table: cmpe138-fa26.cmpe138_project.distract
Distract row count: 436,464
Created table: cmpe138-fa26.cmpe138_project.drimpair
Drimpair row count: 437,770
Created table: cmpe138-fa26.cmpe138_project.factor
Factor row count: 436,643
Created table: cmpe138-fa26.cmpe138_project.safetyeq
Safetyeq row count: 61,098

Duplicate-key checks:
accident: duplicate groups=0, extra duplicate rows=0
vehicle: duplicate groups=0, extra duplicate rows=0
person: duplicate groups=0, extra duplicate rows=0
distract: duplicate groups=0, extra duplicate rows=0
drimpair: duplicate groups=0, extra duplicate rows=0
factor: duplicate groups=0, extra duplicate rows=0
safetyeq: duplicate groups=133, extra duplicate rows=159
```

The `safetyeq` duplicate rows are retained and reported because the source
contains multiple distinct equipment records for some non-motorists. The Phase 2 seed loaded 4,725,767 rows across seven tables. Rerunning the
seed replaces the contents of all seven destination tables using
`WRITE_TRUNCATE`.

## How to Run the Workload

`workload.sql` contains all nine baseline statements. `tuning.sql` creates
the tuned tables, and `workload_after.sql` contains all nine tuned
statements. `measure.py` runs each workload statement three times with
cached results disabled and reports the median elapsed time.

> Fix Q7 in both workload files before running it manually or running
> the full benchmark on a 2000–2018 seed. Its current cleanup deletes
> all 2009 crash rows from the target table, including seeded rows.

Run each statement separately in BigQuery. Before running a statement:

1. Open **Query settings**.
2. Set the processing location to `US`.
3. Clear **Use cached results**.
4. Set a suitable maximum bytes billed limit.
5. Run the query and record the estimated bytes, actual bytes processed, bytes billed and
   elapsed time.

- Question 1 reports fatal crashes and total fatalities by state and year.
- Question 2 reports alcohol-involved fatal-crash percentages by state and year.
- Question 3 reports driver-impairment categories, crash counts, and fatalities
by state and year.
- Question 4 reports total crashes, distracted driving crashes, and fatalities by time of day and year.
- Question 5 compares distracted-driving and impaired-driving counts and percentages by vehicle type and state.
- Question 6 reports injury severity among occupants based on reported safety equipment use across states.
- Question 7 tests inserting historical crash records.
- Question 8 tests updating a crash flag.
- Question 9 looks up historical crashes by state, hour, and year and excludes flagged records.

## How to Start the Application

To come.

## How to Reset

To come.
