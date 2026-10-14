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

print(f"Copying real data into {destination_table}...")

query_job = client.query(query, job_config=job_config)
query_job.result()

table = client.get_table(destination_table)

print(f"Created table: {destination_table}")
print(f"Row count: {table.num_rows:,}")