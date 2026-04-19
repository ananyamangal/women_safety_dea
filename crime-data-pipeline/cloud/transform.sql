CREATE OR REPLACE TABLE `crimedatapipeline.crime_data.processed_data` AS

WITH base AS (
  SELECT
    string_field_0 AS title,
    SAFE.PARSE_TIMESTAMP('%a, %d %b %Y %H:%M:%S %Z', string_field_1) AS date,
    LOWER(CONCAT(string_field_0, " ", string_field_2)) AS text,
    string_field_2 AS description,
    string_field_3 AS source_url
  FROM `crimedatapipeline.crime_data.raw_news`
),

filtered AS (
  SELECT *
  FROM base
  WHERE NOT REGEXP_CONTAINS(text, r"(season|review|netflix|trailer|film|series|show|ott)")
    AND REGEXP_CONTAINS(text, r"(murder|killed|shot|stabbed|rape|assault|theft|robbery|fraud|scam|kidnap)")
),

classified AS (
  SELECT *,
    CASE
      WHEN REGEXP_CONTAINS(text, r"(murder|killed|shot|stabbed)") THEN "Murder"
      WHEN REGEXP_CONTAINS(text, r"(rape|assault|molest)") THEN "Assault"
      WHEN REGEXP_CONTAINS(text, r"(theft|robbery|snatching)") THEN "Theft"
      WHEN REGEXP_CONTAINS(text, r"(kidnap|abduct)") THEN "Kidnapping"
      WHEN REGEXP_CONTAINS(text, r"(fraud|scam|cyber)") THEN "Fraud"
      ELSE "Other"
    END AS crime_type
  FROM filtered
),

located AS (
  SELECT *,
    CASE
      WHEN REGEXP_CONTAINS(text, r"rohini") THEN "rohini"
      WHEN REGEXP_CONTAINS(text, r"dwarka") THEN "dwarka"
      WHEN REGEXP_CONTAINS(text, r"saket") THEN "saket"
      WHEN REGEXP_CONTAINS(text, r"janakpuri") THEN "janakpuri"
      WHEN REGEXP_CONTAINS(text, r"pitampura") THEN "pitampura"
      WHEN REGEXP_CONTAINS(text, r"hauz khas") THEN "hauz khas"
      WHEN REGEXP_CONTAINS(text, r"okhla") THEN "okhla"
      ELSE "delhi"
    END AS location
  FROM classified
)

SELECT DISTINCT *
FROM located;