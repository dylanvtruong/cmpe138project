-- workload-after.sql
-- Same numbering as workload.sql, run against the tables built by tuning.sql.
-- Tables use dataset.table with no project prefix. Location: US.
-- Measure each with "Use cached results" cleared.


-- Question 1 (reads accident_summary instead of accident)
SELECT
  L_YEAR,
  STATE,
  fatal_crash_count,
  total_fatalities
FROM cmpe138_project.accident_summary
WHERE L_YEAR BETWEEN 2010 AND 2018
ORDER BY
  L_YEAR,
  fatal_crash_count DESC,
  STATE;


-- Question 2 (reads accident_summary instead of accident)
SELECT
  L_YEAR,
  STATE,
  fatal_crash_count,
  alcohol_involved_crash_count,
  ROUND(
    100 * alcohol_involved_crash_count / fatal_crash_count,
    2
  ) AS alcohol_involved_percentage
FROM cmpe138_project.accident_summary
WHERE L_YEAR BETWEEN 2010 AND 2018
ORDER BY
  L_YEAR,
  alcohol_involved_percentage DESC,
  STATE;


-- Question 3 (reads drimpair_tuned and accident_tuned)
SELECT
  impairment_records.L_YEAR,
  impairment_records.STATE,
  impairment_records.DRIMPAIR,
  COUNT(*) AS crash_count,
  SUM(accident.FATALS) AS total_fatalities
FROM (
  -- Keep one row for each crash and impairment category.
  SELECT DISTINCT
    L_YEAR,
    STATE,
    ST_CASE,
    DRIMPAIR
  FROM cmpe138_project.drimpair_tuned
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND DRIMPAIR IS NOT NULL
    AND DRIMPAIR != ''
) AS impairment_records
JOIN cmpe138_project.accident_tuned AS accident
  ON impairment_records.L_YEAR = accident.L_YEAR
 AND impairment_records.ST_CASE = accident.ST_CASE
GROUP BY
  impairment_records.L_YEAR,
  impairment_records.STATE,
  impairment_records.DRIMPAIR
ORDER BY
  impairment_records.L_YEAR,
  total_fatalities DESC,
  impairment_records.STATE,
  impairment_records.DRIMPAIR;


-- Question 4 (reads distract_tuned and accident_tuned)
WITH distracted_crashes AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE
  FROM cmpe138_project.distract_tuned
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND MDRDSTRD IS NOT NULL
    AND TRIM(CAST(MDRDSTRD AS STRING)) NOT IN ('', '0')
)

SELECT
  a.L_YEAR,
  CASE
  WHEN a.HOUR BETWEEN 0 AND 5 THEN '00:00-05:59' -- Late Night/Early Morning
  WHEN a.HOUR BETWEEN 6 AND 11 THEN '06:00-11:59' -- Morning
  WHEN a.HOUR BETWEEN 12 AND 17 THEN '12:00-17:59' -- Afternoon
  WHEN a.HOUR BETWEEN 18 AND 23 THEN '18:00-23:59' -- Evening/Night
  ELSE 'Unknown'
  END AS time_of_day,

  COUNT(*) AS total_crashes,
  COUNTIF(d.ST_CASE IS NOT NULL) AS distracted_crashes,
  SUM(a.FATALS) AS total_fatalities,
  SUM(IF(d.ST_CASE IS NOT NULL, a.FATALS, 0)) AS distracted_fatalities
FROM cmpe138_project.accident_tuned AS a
LEFT JOIN distracted_crashes AS d
  ON a.L_YEAR = d.L_YEAR
 AND a.ST_CASE = d.ST_CASE
WHERE a.L_YEAR BETWEEN 2010 AND 2018
GROUP BY a.L_YEAR, time_of_day
ORDER BY a.L_YEAR, distracted_crashes DESC;


-- Question 5 (reads vehicle_tuned, distract_tuned, drimpair_tuned)
WITH distracted AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE,
    VEH_NO
  FROM cmpe138_project.distract_tuned
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND MDRDSTRD IS NOT NULL
    AND TRIM(CAST(MDRDSTRD AS STRING)) NOT IN ('', '0')
),

impaired AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE,
    VEH_NO
  FROM cmpe138_project.drimpair_tuned
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND DRIMPAIR IS NOT NULL
    AND TRIM(CAST(DRIMPAIR AS STRING)) NOT IN ('', '0')
)

SELECT
  v.STATE,
  v.BODY_TYP AS vehicle_type,
  COUNTIF(d.ST_CASE IS NOT NULL) AS distracted_vehicles,
  COUNTIF(i.ST_CASE IS NOT NULL) AS impaired_vehicles,

  ROUND(
    100 * COUNTIF(d.ST_CASE IS NOT NULL) / COUNT(*),
    2
  ) AS distracted_percentage,

  ROUND(
    100 * COUNTIF(i.ST_CASE IS NOT NULL) / COUNT(*),
    2
  ) AS impaired_percentage

FROM cmpe138_project.vehicle_tuned AS v
LEFT JOIN distracted AS d
  ON v.L_YEAR = d.L_YEAR
 AND v.ST_CASE = d.ST_CASE
 AND v.VEH_NO = d.VEH_NO
LEFT JOIN impaired AS i
  ON v.L_YEAR = i.L_YEAR
 AND v.ST_CASE = i.ST_CASE
 AND v.VEH_NO = i.VEH_NO
WHERE v.L_YEAR BETWEEN 2010 AND 2018
GROUP BY v.STATE, vehicle_type
ORDER BY v.STATE, distracted_percentage DESC, impaired_percentage DESC;


-- Question 6 (reads person_tuned)
SELECT
  STATE,
  REST_USE AS safety_equipment,
  COUNT(*) AS total_occupants,

  COUNTIF(
    SAFE_CAST(INJ_SEV AS INT64) IN (3,4)) AS fatal_or_severe_injuries,

  ROUND(
    100 * COUNTIF(SAFE_CAST(INJ_SEV AS INT64) IN (3,4)) / COUNT(*),
    2
  ) AS fatal_or_severe_percentage

FROM cmpe138_project.person_tuned

WHERE L_YEAR BETWEEN 2010 AND 2018
  AND REST_USE IS NOT NULL

GROUP BY STATE, safety_equipment
ORDER BY STATE, fatal_or_severe_percentage DESC;


-- Question 7 (inserts into accident_tuned)
-- Price this together with the summary refresh: after a real insert,
-- accident_summary is stale until the Change 1 statement in tuning.sql
-- is rerun. Refresh cost x its frequency belongs in Part C step 5.
INSERT INTO cmpe138_project.accident_tuned
  (L_YEAR, STATE, ST_CASE, FATALS, DRUNK_DR, HOUR)
SELECT
  L_YEAR, STATE, ST_CASE, FATALS, DRUNK_DR, HOUR
FROM `bigquery-public-data.dataflix_traffic_safety.accident`
WHERE L_YEAR = 2009;

-- Put it back before the next measurement:
-- DELETE FROM cmpe138_project.accident_tuned WHERE L_YEAR = 2009;


-- Question 8 (updates accident_tuned; pays for one year's partition)
UPDATE cmpe138_project.accident_tuned
SET is_flagged = TRUE
WHERE L_YEAR = 2015
  AND ST_CASE = 60001;

-- Put it back before the next measurement:
-- UPDATE cmpe138_project.accident_tuned SET is_flagged = NULL
-- WHERE L_YEAR = 2015 AND ST_CASE = 60001;


-- Question 9 (reads accident_tuned)
-- MONTH is not in the seeded slice, so this filters on state and hour only.
SELECT
  L_YEAR,
  COUNT(*) AS fatal_crash_count,
  IFNULL(SUM(FATALS), 0) AS total_fatalities,
  COUNTIF(IFNULL(DRUNK_DR, 0) > 0) AS alcohol_involved_crash_count
FROM cmpe138_project.accident_tuned
WHERE STATE = 'California'
  AND HOUR = 22
  AND L_YEAR BETWEEN 2010 AND 2018
  AND NOT IFNULL(is_flagged, FALSE)
GROUP BY
  L_YEAR
ORDER BY
  L_YEAR;