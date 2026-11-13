import os
from google.cloud import bigquery


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

if not PROJECT_ID:
    raise SystemExit(
        "GCP_PROJECT_ID is not set. Run: "
        '$env:GCP_PROJECT_ID = "cmpe138-testproj1"'
    )


KEY_COLUMNS = {
    "accident": ["L_YEAR", "ST_CASE"],
    "vehicle": ["L_YEAR", "ST_CASE", "VEH_NO"],
    "person": ["L_YEAR", "ST_CASE", "VEH_NO", "PER_NO"],
    "distract": ["L_YEAR", "ST_CASE", "VEH_NO", "MDRDSTRD"],
    "drimpair": ["L_YEAR", "ST_CASE", "VEH_NO", "DRIMPAIR"],
    "factor": ["L_YEAR", "ST_CASE", "VEH_NO", "MFACTOR"],
    "safetyeq": ["L_YEAR", "ST_CASE", "VEH_NO", "PER_NO"],
}


PRIMARY_KEYS = {
    "accident": "(L_YEAR, ST_CASE)",
    "vehicle": "(L_YEAR, ST_CASE, VEH_NO)",
    "person": "(L_YEAR, ST_CASE, VEH_NO, PER_NO)",
    "distract": "(L_YEAR, ST_CASE, VEH_NO, MDRDSTRD)",
    "drimpair": "(L_YEAR, ST_CASE, VEH_NO, DRIMPAIR)",
    "factor": "(L_YEAR, ST_CASE, VEH_NO, MFACTOR)",
    "safetyeq": "(L_YEAR, ST_CASE, VEH_NO, PER_NO)",
}


FOREIGN_KEYS = [
    ("vehicle", "(L_YEAR, ST_CASE)", "accident"),
    ("distract", "(L_YEAR, ST_CASE, VEH_NO)", "vehicle"),
    ("drimpair", "(L_YEAR, ST_CASE, VEH_NO)", "vehicle"),
    ("factor", "(L_YEAR, ST_CASE, VEH_NO)", "vehicle"),
    ("safetyeq", "(L_YEAR, ST_CASE, VEH_NO, PER_NO)", "person"),
]


def add_constraints(client):
    """Declare Phase 2 keys after all seven tables have been rebuilt."""
    for table_name, columns in PRIMARY_KEYS.items():
        query = f"""
ALTER TABLE `{PROJECT_ID}.{DATASET_ID}.{table_name}`
ADD PRIMARY KEY {columns} NOT ENFORCED
"""
        client.query(query, location="US").result()

    for child_table, child_columns, parent_table in FOREIGN_KEYS:
        query = f"""
ALTER TABLE `{PROJECT_ID}.{DATASET_ID}.{child_table}`
ADD FOREIGN KEY {child_columns}
REFERENCES `{PROJECT_ID}.{DATASET_ID}.{parent_table}`
{PRIMARY_KEYS[parent_table]}
NOT ENFORCED
"""
        client.query(query, location="US").result()


def duplicate_count_query(table_name):
    """Return a query counting duplicate groups and extra duplicate rows."""
    columns = ", ".join(KEY_COLUMNS[table_name])
    return f"""
SELECT
  COUNT(*) AS duplicate_key_groups,
  COALESCE(SUM(row_count - 1), 0) AS duplicate_extra_rows
FROM (
  SELECT
    {columns},
    COUNT(*) AS row_count
  FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
  GROUP BY {columns}
  HAVING COUNT(*) > 1
)
"""

DATASET_ID = "cmpe138_project"
START_YEAR = int(os.environ.get("FARS_START_YEAR", "2010"))
END_YEAR = int(os.environ.get("FARS_END_YEAR", "2018"))
MAX_BYTES_BILLED = int(
    os.environ.get("MAX_BYTES_BILLED", "150000000")
)
YEAR_FILTER = f"WHERE L_YEAR BETWEEN {START_YEAR} AND {END_YEAR}"

ACCIDENT_TABLE_ID = "accident"
VEHICLE_TABLE_ID = "vehicle"
PERSON_TABLE_ID = "person"
DISTRACT_TABLE_ID = "distract"
DRIMPAIR_TABLE_ID = "drimpair"
FACTOR_TABLE_ID = "factor"
SAFETYEQ_TABLE_ID = "safetyeq"

# Destination tables
accident_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{ACCIDENT_TABLE_ID}"
)
vehicle_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{VEHICLE_TABLE_ID}"
)
person_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{PERSON_TABLE_ID}"
)
distract_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{DISTRACT_TABLE_ID}"
)
drimpair_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{DRIMPAIR_TABLE_ID}"
)
factor_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{FACTOR_TABLE_ID}"
)
safetyeq_destination_table = (
    f"{PROJECT_ID}.{DATASET_ID}.{SAFETYEQ_TABLE_ID}"
)

# BigQuery client and dataset creation
client = bigquery.Client(project=PROJECT_ID)

# Create the destination dataset if it does not already exist.
dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
dataset.location = "US"
client.create_dataset(dataset, exists_ok=True)

accident_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  COUNTY,
  CITY,
  HOUR,
  FATALS,
  DRUNK_DR,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.accident`
{YEAR_FILTER}
"""

vehicle_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  BODY_TYP,
  NUMOCCS,
  DEATHS,
  DR_DRINK,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.vehicle`
{YEAR_FILTER}
"""

person_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  PER_NO,
  PER_TYP,
  INJ_SEV,
  REST_USE,
  AIR_BAG,
  AGE,
  SEX,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.person`
{YEAR_FILTER}
"""

distract_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  MDRDSTRD,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.distract`
{YEAR_FILTER}
"""

drimpair_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  DRIMPAIR,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.drimpair`
{YEAR_FILTER}
"""

factor_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  MFACTOR,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.factor`
{YEAR_FILTER}
"""

safetyeq_query = f"""
SELECT
  L_YEAR,
  STATE,
  ST_CASE,
  VEH_NO,
  PER_NO,
  NMHELMET,
  NMPROPAD,
  NMOTHPRO,
  NMREFCLO,
  NMLIGHT,
  NMOTHPRE,
  DATE_PARTITION
FROM `bigquery-public-data.dataflix_traffic_safety.safetyeq`
{YEAR_FILTER}
"""

job_config = bigquery.QueryJobConfig(
    destination=accident_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

# Validate the query and estimate how much data it will read.
dry_run_config = bigquery.QueryJobConfig(
    dry_run=True,
    use_query_cache=False,
)

dry_run_job = client.query(
    accident_query,
    job_config=dry_run_config,
    location="US",
)

estimated_bytes = dry_run_job.total_bytes_processed
billing_limit = job_config.maximum_bytes_billed

vehicle_job_config = bigquery.QueryJobConfig(
    destination=vehicle_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

person_job_config = bigquery.QueryJobConfig(
    destination=person_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

distract_job_config = bigquery.QueryJobConfig(
    destination=distract_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

drimpair_job_config = bigquery.QueryJobConfig(
    destination=drimpair_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

factor_job_config = bigquery.QueryJobConfig(
    destination=factor_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

safetyeq_job_config = bigquery.QueryJobConfig(
    destination=safetyeq_destination_table,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    maximum_bytes_billed=MAX_BYTES_BILLED,
)

vehicle_dry_run_job = client.query(
    vehicle_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

vehicle_estimated_bytes = vehicle_dry_run_job.total_bytes_processed

person_dry_run_job = client.query(
    person_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

person_estimated_bytes = person_dry_run_job.total_bytes_processed

distract_dry_run_job = client.query(
    distract_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

distract_estimated_bytes = distract_dry_run_job.total_bytes_processed

drimpair_dry_run_job = client.query(
    drimpair_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

drimpair_estimated_bytes = drimpair_dry_run_job.total_bytes_processed

factor_dry_run_job = client.query(
    factor_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

factor_estimated_bytes = factor_dry_run_job.total_bytes_processed

safetyeq_dry_run_job = client.query(
    safetyeq_query,
    job_config=bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    ),
    location="US",
)

safetyeq_estimated_bytes = safetyeq_dry_run_job.total_bytes_processed

print(f"Seed year range: {START_YEAR}-{END_YEAR}")
print(f"Accident destination: {accident_destination_table}")
print(f"Accident estimated bytes: {estimated_bytes:,}")
print(f"Vehicle destination: {vehicle_destination_table}")
print(f"Vehicle estimated bytes: {vehicle_estimated_bytes:,}")
print(f"Person destination: {person_destination_table}")
print(f"Person estimated bytes: {person_estimated_bytes:,}")
print(f"Distract destination: {distract_destination_table}")
print(f"Distract estimated bytes: {distract_estimated_bytes:,}")
print(f"Drimpair destination: {drimpair_destination_table}")
print(f"Drimpair estimated bytes: {drimpair_estimated_bytes:,}")
print(f"Factor destination: {factor_destination_table}")
print(f"Factor estimated bytes: {factor_estimated_bytes:,}")
print(f"Safetyeq destination: {safetyeq_destination_table}")
print(f"Safetyeq estimated bytes: {safetyeq_estimated_bytes:,}")
print(f"Maximum bytes billed: {billing_limit:,}")

if estimated_bytes > billing_limit:
    raise SystemExit(
        "The estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if vehicle_estimated_bytes > vehicle_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The vehicle estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if person_estimated_bytes > person_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The person estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if distract_estimated_bytes > distract_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The distract estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if drimpair_estimated_bytes > drimpair_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The drimpair estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if factor_estimated_bytes > factor_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The factor estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

if safetyeq_estimated_bytes > safetyeq_job_config.maximum_bytes_billed:
    raise SystemExit(
        "The safetyeq estimate exceeds the billing limit. "
        "Reduce the data slice before running."
    )

# WRITE_TRUNCATE replaces the destination table on each run.
answer = input(
    "Copy all seven data tables and replace all tables? [y/N]: "
)

if answer.strip().lower() != "y":
    raise SystemExit("Seed cancelled.")

print(f"Copying real data into {accident_destination_table}...")

query_job = client.query(
    accident_query,
    job_config=job_config,
    location="US",
)
query_job.result()

print(f"Copying real data into {vehicle_destination_table}...")

vehicle_query_job = client.query(
    vehicle_query,
    job_config=vehicle_job_config,
    location="US",
)
vehicle_query_job.result()

print(f"Copying real data into {person_destination_table}...")

person_query_job = client.query(
    person_query,
    job_config=person_job_config,
    location="US",
)
person_query_job.result()

print(f"Copying real data into {distract_destination_table}...")

distract_query_job = client.query(
    distract_query,
    job_config=distract_job_config,
    location="US",
)
distract_query_job.result()

print(f"Copying real data into {drimpair_destination_table}...")

drimpair_query_job = client.query(
    drimpair_query,
    job_config=drimpair_job_config,
    location="US",
)
drimpair_query_job.result()

print(f"Copying real data into {factor_destination_table}...")

factor_query_job = client.query(
    factor_query,
    job_config=factor_job_config,
    location="US",
)
factor_query_job.result()

print(f"Copying real data into {safetyeq_destination_table}...")

safetyeq_query_job = client.query(
    safetyeq_query,
    job_config=safetyeq_job_config,
    location="US",
)
safetyeq_query_job.result()

client.query(
    f"""
    ALTER TABLE `{accident_destination_table}`
    ADD COLUMN IF NOT EXISTS is_flagged BOOL
    """,
    location="US",
).result()

print("Adding non-enforced primary and foreign keys...")
add_constraints(client)

accident_table = client.get_table(accident_destination_table)
vehicle_table = client.get_table(vehicle_destination_table)
person_table = client.get_table(person_destination_table)
distract_table = client.get_table(distract_destination_table)
drimpair_table = client.get_table(drimpair_destination_table)
factor_table = client.get_table(factor_destination_table)
safetyeq_table = client.get_table(safetyeq_destination_table)

print("\nSeed completed.")
print(f"Created table: {accident_destination_table}")
print(f"Accident row count: {accident_table.num_rows:,}")
print(f"Created table: {vehicle_destination_table}")
print(f"Vehicle row count: {vehicle_table.num_rows:,}")
print(f"Created table: {person_destination_table}")
print(f"Person row count: {person_table.num_rows:,}")
print(f"Created table: {distract_destination_table}")
print(f"Distract row count: {distract_table.num_rows:,}")
print(f"Created table: {drimpair_destination_table}")
print(f"Drimpair row count: {drimpair_table.num_rows:,}")
print(f"Created table: {factor_destination_table}")
print(f"Factor row count: {factor_table.num_rows:,}")
print(f"Created table: {safetyeq_destination_table}")
print(f"Safetyeq row count: {safetyeq_table.num_rows:,}")

print("\nDuplicate-key checks:")
for table_name in KEY_COLUMNS:
    duplicate_job = client.query(
        duplicate_count_query(table_name),
        job_config=bigquery.QueryJobConfig(
            use_query_cache=False,
            maximum_bytes_billed=billing_limit,
        ),
        location="US",
    )
    duplicate_row = next(iter(duplicate_job.result()))
    print(
        f"{table_name}: "
        f"duplicate groups={duplicate_row.duplicate_key_groups:,}, "
        f"extra duplicate rows={duplicate_row.duplicate_extra_rows:,}"
    )

if (
    accident_table.num_rows == 0
    or vehicle_table.num_rows == 0
    or person_table.num_rows == 0
    or distract_table.num_rows == 0
    or drimpair_table.num_rows == 0
    or factor_table.num_rows == 0
    or safetyeq_table.num_rows == 0
):
    raise SystemExit("Seed validation failed: at least one destination table is empty.")
