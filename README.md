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

The seed script copies selected real FARS traffic-safety data from 2010 through
2018 into the `cmpe138_project` dataset. It loads seven related tables:

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
dry-run byte estimates, uses a maximum of 150,000,000 bytes billed per table,
asks for confirmation before replacing the destination tables, declares
non-enforced primary and foreign keys, and prints duplicate-key counts.

Seed command:

```powershell
$env:GCP_PROJECT_ID = "cmpe138-fa26"
python seed.py
```

Seed output:

```text
Copy all seven data tables and replace all tables? [y/N]: y

Adding non-enforced primary and foreign keys...
Seed completed.
Created table: cmpe138-fa26.cmpe138_project.accident
Accident row count: 289,074
Created table: cmpe138-fa26.cmpe138_project.vehicle
Vehicle row count: 434,970
Created table: cmpe138-fa26.cmpe138_project.person
Person row count: 714,503
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
contains multiple distinct equipment records for some non-motorists. The seed
is safe to run again because each destination table uses `WRITE_TRUNCATE`.

The current seeded row counts total 2,810,522 rows across the seven tables.

## How to Run the Workload

The numbered workload statements are stored in `workload.sql` and correspond
to the nine project questions.

Questions 1–6 currently have working SQL statements. Questions 7–9 are listed
in the file and will be implemented next.

Run each statement separately in BigQuery. Before running a statement:

1. Open **Query settings**.
2. Set the processing location to `US`.
3. Clear **Use cached results**.
4. Set a suitable maximum bytes billed limit.
5. Run the query and record the estimated bytes, actual bytes processed, and
   elapsed time.

- Question 1 reports fatal crashes and total fatalities by state and year.
- Question 2 reports alcohol-involved fatal-crash percentages by state and year.
- Question 3 reports driver-impairment categories, crash counts, and fatalities
by state and year.
- Question 4 reports total crashes, distracted driving crashes, and fatalities by time of day and year.
- Question 5 reports distracted driving to impaired driving vehicle based on counts and percentages by vehicle type and state.
- Question 6 reports injury severity among occupants based on reported safety equipment use across states.

## How to Start the Application

To come.

## How to Reset

To come.
