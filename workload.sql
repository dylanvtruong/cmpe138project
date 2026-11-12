-- Question 1
-- What states had the most fatal crashes between 2010 and 2018,
-- and how did trends vary over time?

SELECT
  L_YEAR,
  STATE,
  COUNT(*) AS fatal_crash_count,
  IFNULL(SUM(FATALS), 0) AS total_fatalities
FROM `cmpe138-fa26.cmpe138_project.accident`
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
-- - alcohol_involved_percentage is the percentage of fatal crashes involving at least one recorded alcohol-impaired driver.
-- - The query includes the counts alongside percentages, which is useful because small states can have unstable percentages.
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
FROM `cmpe138-fa26.cmpe138_project.accident`
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
  FROM `cmpe138-fa26.cmpe138_project.drimpair`
  WHERE L_YEAR BETWEEN 2010 AND 2018
    AND DRIMPAIR IS NOT NULL
    AND DRIMPAIR != ''
) AS impairment_records
JOIN `cmpe138-fa26.cmpe138_project.accident` AS accident
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


-- Question 5
-- Does vehicle type correlate with a higher rate of distracted or impaired
-- driving across states?


-- Question 6
-- Which types of occupant safety equipment were associated with the highest
-- and lowest percentages of fatal or severe injuries, and how did these
-- patterns vary by state?


-- Question 7
-- Can a new release of crash records be inserted into the database without
-- replacing the existing 2010-2018 records?


-- Question 8
-- Can a user flag an incorrect crash record so that it is excluded from
-- future reports?


-- Question 9
-- Can a user enter a state, month, and hour of travel and compare those
-- conditions with historical fatal-crash patterns?

-- crash_count: number of distinct crashes associated with that impairment category.
-- total_fatalities: sum of fatalities from those crashes.
-- DRIMPAIR: the recorded impairment category.

