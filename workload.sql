-- Question 1
-- What states had the most fatal crashes between 2010 and 2018,
-- and how did trends vary over time?

SELECT
  L_YEAR,
  STATE,
  COUNT(*) AS fatal_crash_count,
  IFNULL(SUM(FATALS), 0) AS total_fatalities
FROM cmpe138_project.accident
WHERE L_YEAR BETWEEN 2010 AND 2018
GROUP BY
  L_YEAR,
  STATE
ORDER BY
  L_YEAR,
  fatal_crash_count DESC,
  STATE;

-- Texas, California, and Florida have the highest fatal-crash counts.
-- Results are grouped separately by year.
-- fatal_crash_count counts crashes.
-- total_fatalities counts people killed.
-- The result includes Puerto Rico, so describe the output as states/territories if needed.



-- Question 2
-- What percentage of fatal crashes involved an alcohol-impaired driver
-- in each state between 2010 and 2018?
-- The denominator is the number of fatal crashes in the accident table.

-- Important interpretation:
-- - fatal_crash_count is the denominator.
-- - alcohol_involved_crash_count counts crashes where DRUNK_DR > 0.
-- - The alcohol-involved percentage uses crashes with at least one recorded alcohol-impaired driver.
-- - The query includes counts because percentages for small states can be unstable.
-- - Missing DRUNK_DR values are treated as zero by IFNULL.

SELECT
  L_YEAR,
  STATE,
  COUNT(*) AS fatal_crash_count,
  COUNTIF(IFNULL(DRUNK_DR, 0) > 0) AS alcohol_involved_crash_count,
  ROUND(
    100 * COUNTIF(IFNULL(DRUNK_DR, 0) > 0) / COUNT(*),
    2
  ) AS alcohol_involved_percentage
FROM cmpe138_project.accident
WHERE L_YEAR BETWEEN 2010 AND 2018
GROUP BY
  L_YEAR,
  STATE
ORDER BY
  L_YEAR,
  alcohol_involved_percentage DESC,
  STATE;


-- Question 3
-- Which driver-impairment categories were associated with the highest
-- number of fatalities, and how did the pattern vary by state and year?

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
  FROM cmpe138_project.drimpair AS dr
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND DRIMPAIR IS NOT NULL
    AND DRIMPAIR != ''
) AS impairment_records
JOIN cmpe138_project.accident AS accident
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


-- Question 4
-- How does the time of day impact the presence and severity of distracted
-- driving accidents?
WITH distracted_crashes AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE
  FROM cmpe138_project.distract
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
FROM cmpe138_project.accident AS a
LEFT JOIN distracted_crashes AS d
  ON a.L_YEAR = d.L_YEAR
 AND a.ST_CASE = d.ST_CASE
WHERE a.L_YEAR BETWEEN 2010 AND 2018
GROUP BY a.L_YEAR, time_of_day
ORDER BY a.L_YEAR, distracted_crashes DESC;

-- Question 5
-- Does vehicle type correlate with a higher rate of distracted or impaired
-- driving across states?
WITH distracted AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE,
    VEH_NO
  FROM cmpe138_project.distract
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND MDRDSTRD IS NOT NULL
    AND TRIM(CAST(MDRDSTRD AS STRING)) NOT IN ('', '0')
),

impaired AS (
  SELECT DISTINCT
    L_YEAR,
    ST_CASE,
    VEH_NO
  FROM cmpe138_project.drimpair AS dr
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

FROM cmpe138_project.vehicle AS v
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

-- Question 6
-- Which types of occupant safety equipment were associated with the highest
-- and lowest percentages of fatal or severe injuries, and how did these
-- patterns vary by state?
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

FROM cmpe138_project.person

WHERE L_YEAR BETWEEN 2010 AND 2018
  AND REST_USE IS NOT NULL

GROUP BY STATE, safety_equipment
ORDER BY STATE, fatal_or_severe_percentage DESC;


-- Question 7
-- Can a new release of crash records be inserted into the database without
-- replacing the existing 2010-2018 records?
-- Inserts a year outside the seeded range (2009 here). Pick any year that is
-- not already in your table. List every column your seed copied.
INSERT INTO cmpe138_project.accident
  (L_YEAR, STATE, ST_CASE, FATALS, DRUNK_DR, HOUR)
SELECT
  L_YEAR, STATE, ST_CASE, FATALS, DRUNK_DR, HOUR
FROM `bigquery-public-data.dataflix_traffic_safety.accident`
WHERE L_YEAR = 2009;
 
-- Put it back before the next measurement:
-- DELETE FROM cmpe138_project.accident WHERE L_YEAR = 2009;

-- Question 8
-- Can a user flag an incorrect crash record so that it is excluded from
-- future reports?
-- Replace the literals with a real (L_YEAR, ST_CASE) from your table.
UPDATE cmpe138_project.accident
SET is_flagged = TRUE
WHERE L_YEAR = 2015
  AND ST_CASE = 60001;
 
-- Put it back before the next measurement:
-- UPDATE cmpe138_project.accident SET is_flagged = NULL
-- WHERE L_YEAR = 2015 AND ST_CASE = 60001;
 
 
-- Question 9
-- Can a user enter a state, month, and hour of travel and compare those
-- conditions with historical fatal-crash patterns?
-- MONTH is not in the seeded slice, so this filters on state and hour only.
-- Literals stand in for user input. Check the STATE type in your schema:
-- if it is a numeric code, use 6 instead of 'California'.
SELECT
  L_YEAR,
  COUNT(*) AS fatal_crash_count,
  IFNULL(SUM(FATALS), 0) AS total_fatalities,
  COUNTIF(IFNULL(DRUNK_DR, 0) > 0) AS alcohol_involved_crash_count
FROM cmpe138_project.accident
WHERE STATE = 'California'
  AND HOUR = 22
  AND L_YEAR BETWEEN 2010 AND 2018
  AND NOT IFNULL(is_flagged, FALSE)
GROUP BY
  L_YEAR
ORDER BY
  L_YEAR;
