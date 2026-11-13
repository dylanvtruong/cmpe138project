-- tuning.sql
-- Run AFTER seed.py. Builds tuned copies under new names so the original
-- ("before") tables stay untouched and both designs sit side by side.
-- Tables are referenced as dataset.table with no project prefix, so this runs
-- in whichever project the console / bq tool is set to. Processing location: US.
--
-- Prerequisite: seed.py must already have added accident.is_flagged
--   (ALTER TABLE cmpe138_project.accident ADD COLUMN IF NOT EXISTS is_flagged BOOL;)
-- before this runs, so accident_tuned inherits the column.
--
-- Price every CREATE below in Part C step 5 (one-time rebuild = bytes processed).


-- Change 1: summary table for Q1 and Q2
-- Both statements scan accident and GROUP BY (L_YEAR, STATE). The result is
-- about one row per state per year, so both can read this table instead.
-- Staleness risk: Q7 inserts and Q8 flags change accident but not this table
-- until it is rebuilt. Refresh cost = rerun this statement x its frequency.
CREATE OR REPLACE TABLE cmpe138_project.accident_summary AS
SELECT
  L_YEAR,
  STATE,
  COUNT(*) AS fatal_crash_count,
  IFNULL(SUM(FATALS), 0) AS total_fatalities,
  COUNTIF(IFNULL(DRUNK_DR, 0) > 0) AS alcohol_involved_crash_count
FROM cmpe138_project.accident
GROUP BY
  L_YEAR,
  STATE;


-- Change 2: partition + cluster accident (Q3, Q4, Q8, Q9)
-- Q3 and Q4 filter on L_YEAR and join on (L_YEAR, ST_CASE); Q9 filters on STATE;
-- Q8 updates one crash by (L_YEAR, ST_CASE). Partitioning by year means an
-- UPDATE pays for one partition instead of the whole table.
-- L_YEAR must be INT64 for integer-range partitioning.
-- If your seed also copied MONTH and HOUR, consider
--   CLUSTER BY STATE, MONTH, HOUR, ST_CASE
-- since Q9 filters on all three. Order matters: STATE first.
CREATE OR REPLACE TABLE cmpe138_project.accident_tuned
PARTITION BY RANGE_BUCKET(L_YEAR, GENERATE_ARRAY(2000, 2030, 1))
CLUSTER BY STATE, ST_CASE
AS SELECT * FROM cmpe138_project.accident;


-- Change 3: partition + cluster person (Q6)
-- Q6 filters on L_YEAR and REST_USE and groups by (STATE, REST_USE).
-- person is the largest table, above the 64 MB level where clustering is
-- expected to help.
CREATE OR REPLACE TABLE cmpe138_project.person_tuned
PARTITION BY RANGE_BUCKET(L_YEAR, GENERATE_ARRAY(2000, 2030, 1))
CLUSTER BY REST_USE, STATE
AS SELECT * FROM cmpe138_project.person;


-- Change 4 (optional): cluster the tables joined by Q3, Q4 and Q5
-- These join on (L_YEAR, ST_CASE, VEH_NO). Expect bytes to move little,
-- since Q3-Q5 filter on the whole seeded year range. A result that did not
-- move is still a result: check the join stage in the query plan.
CREATE OR REPLACE TABLE cmpe138_project.vehicle_tuned
PARTITION BY RANGE_BUCKET(L_YEAR, GENERATE_ARRAY(2000, 2030, 1))
CLUSTER BY ST_CASE, VEH_NO
AS SELECT * FROM cmpe138_project.vehicle;

CREATE OR REPLACE TABLE cmpe138_project.distract_tuned
PARTITION BY RANGE_BUCKET(L_YEAR, GENERATE_ARRAY(2000, 2030, 1))
CLUSTER BY ST_CASE, VEH_NO
AS SELECT * FROM cmpe138_project.distract;

CREATE OR REPLACE TABLE cmpe138_project.drimpair_tuned
PARTITION BY RANGE_BUCKET(L_YEAR, GENERATE_ARRAY(2000, 2030, 1))
CLUSTER BY ST_CASE, VEH_NO
AS SELECT * FROM cmpe138_project.drimpair;