CREATE OR REPLACE TABLE `crimedatapipeline.crime_data.final_data` AS

WITH freq AS (
  SELECT location, COUNT(*) AS frequency
  FROM `crimedatapipeline.crime_data.processed_data`
  GROUP BY location
),

scored AS (
  SELECT
    p.*,
    f.frequency,

    CASE
      WHEN crime_type = "Murder" THEN 5
      WHEN crime_type = "Assault" THEN 4
      WHEN crime_type = "Kidnapping" THEN 4
      WHEN crime_type = "Theft" THEN 2
      ELSE 1
    END AS severity,

    CASE
      WHEN date IS NULL THEN 1
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(date), DAY) < 7 THEN 5
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(date), DAY) < 30 THEN 4
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(date), DAY) < 90 THEN 3
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(date), DAY) < 180 THEN 2
      ELSE 1
    END AS recency

  FROM `crimedatapipeline.crime_data.processed_data` p
  JOIN freq f USING(location)
)

SELECT *,
  ROUND(
    1 / (1 + 0.5*frequency + 0.3*severity + 0.2*recency),
    4
  ) AS safety_score
FROM scored;