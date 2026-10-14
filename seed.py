import os

from google.cloud import bigquery


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

if not PROJECT_ID:
    raise SystemExit(
        "GCP_PROJECT_ID is not set. Run: "
        '$env:GCP_PROJECT_ID = "cmpe138-fa26"'
    )

DATASET_ID = "cmpe138_project"
TABLE_ID = "accident"

destination_table = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

client = bigquery.Client(project=PROJECT_ID)

# Create the destination dataset if it does not already exist.
dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
dataset.location = "US"
client.create_dataset(dataset, exists_ok=True)

query = """
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  COUNTY,
  CITY,
  FATALS,
  DRUNK_DR,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.accident`
WHERE DATE_PARTITION = DATE '2017-01-01'
"""

job_config = bigquery.QueryJobConfig(
    destination=destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=150_000_000,
)

# Validate the query and estimate how much data it will read.
dry_run_config = bigquery.QueryJobConfig(
    dry_run=True,
    use_query_cache=False,
)

dry_run_job = client.query(
    query,
    job_config=dry_run_config,
    location="US",
)

estimated_bytes = dry_run_job.total_bytes_processed
billing_limit = job_config.maximum_bytes_billed

print(f"Destination: {destination_table}")
print(f"Estimated bytes processed: {estimated_bytes:,}")
print(f"Maximum bytes billed: {billing_limit:,}")

if estimated_bytes > billing_limit:
    raise SystemExit(
        "The estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

# WRITE_TRUNCATE replaces the destination table on each run.
answer = input(
    "Copy the data and replace the destination table? [y/N]: "
)

if answer.strip().lower() != "y":
    raise SystemExit("Seed cancelled.")

print(f"Copying real data into {destination_table}...")

query_job = client.query(
    query,
    job_config=job_config,
    location="US",
)
query_job.result()

table = client.get_table(destination_table)

print("\nSeed completed.")
print(f"Created table: {destination_table}")
print(f"Row count: {table.num_rows:,}")

if table.num_rows == 0:
    print("WARNING: No rows were copied. Check the source filter.")