# CMPE 138 Traffic Safety Project

## What the Application Is

This application uses real traffic-safety data from the BigQuery public dataset:

`bigquery-public-data.dataflix_traffic_safety`

The dataset includes details on fatal crashes, road conditions, and vehicle types categorized by state, year, and roadway.

The project copies selected traffic-safety data into a BigQuery dataset named `cmpe138_project` for analysis.

## System Diagram

To come.

## What to Install

To come.

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

The seed script copies real 2017 accident data from the BigQuery public dataset into the `cmpe138_project` dataset.

The source table is:

```text
bigquery-public-data.dataflix_traffic_safety.accident
```

The destination table is:

```text
cmpe138-fa26.cmpe138_project.accident
```

The seed script copies selected columns from 34,528 real accident records.

Seed command:

```powershell
$env:GCP_PROJECT_ID = "cmpe138-fa26"
python seed.py
```

Seed output:

```text
Destination: cmpe138-fa26.cmpe138_project.accident
Estimated bytes processed: 115,453,915
Maximum bytes billed: 150,000,000
Copy the data and replace the destination table? [y/N]: y
Copying real data into cmpe138-fa26.cmpe138_project.accident...

Seed completed.
Created table: cmpe138-fa26.cmpe138_project.accident
Row count: 34,528
```

## How to Run the Workload

To come.

## How to Start the Application

To come.

## How to Reset

To come.
