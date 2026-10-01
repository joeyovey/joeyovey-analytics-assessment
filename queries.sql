-- DATA QUALITY AUDIT

-- 1. Count all records in the table
SELECT COUNT(*) AS total_records
FROM food_prices;


-- 2. Check for null values in each column
SELECT
    COUNT(*) FILTER (WHERE countryiso3 IS NULL) AS countryiso3_nulls,
    COUNT(*) FILTER (WHERE date IS NULL) AS date_nulls,
    COUNT(*) FILTER (WHERE admin1 IS NULL) AS admin1_nulls,
    COUNT(*) FILTER (WHERE admin2 IS NULL) AS admin2_nulls,
    COUNT(*) FILTER (WHERE market IS NULL) AS market_nulls,
    COUNT(*) FILTER (WHERE market_id IS NULL) AS market_id_nulls,
    COUNT(*) FILTER (WHERE latitude IS NULL) AS latitude_nulls,
    COUNT(*) FILTER (WHERE longitude IS NULL) AS longitude_nulls,
    COUNT(*) FILTER (WHERE category IS NULL) AS category_nulls,
    COUNT(*) FILTER (WHERE commodity IS NULL) AS commodity_nulls,
    COUNT(*) FILTER (WHERE commodity_id IS NULL) AS commodity_id_nulls,
    COUNT(*) FILTER (WHERE unit IS NULL) AS unit_nulls,
    COUNT(*) FILTER (WHERE priceflag IS NULL) AS priceflag_nulls,
    COUNT(*) FILTER (WHERE pricetype IS NULL) AS pricetype_nulls,
    COUNT(*) FILTER (WHERE currency IS NULL) AS currency_nulls,
    COUNT(*) FILTER (WHERE price IS NULL) AS price_nulls,
    COUNT(*) FILTER (WHERE usdprice IS NULL) AS usdprice_nulls
FROM food_prices;

-- Null values found in these columns:
-- admin1: 138, admin2: 138, latitude: 138,
-- longitude: 138, price: 757


-- 3. Check for duplicate records
SELECT
    countryiso3, date, market, commodity, unit, currency, price,
    COUNT(*) AS duplicate_count
FROM food_prices
GROUP BY
    countryiso3, date, market, commodity, unit, currency, price
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- A duplicate is a record with the same key values.
-- These records may represent repeated data points.


-- 4. Check the date range of the data
SELECT MIN(date) AS start_date, MAX(date) AS end_date
FROM food_prices;

-- The query shows the earliest and latest dates in the dataset.


-- 5. Find country and commodity pairs with the most records
SELECT countryiso3, commodity, COUNT(*) AS record_count
FROM food_prices
GROUP BY countryiso3, commodity
ORDER BY record_count DESC
LIMIT 5;


-- A-2: ANALYTICAL SQL

-- 2.1 Find the 10 commodities with the largest price increase
SELECT commodity,

    -- Average price in the first year
    ROUND(
        AVG(price) FILTER (
            WHERE EXTRACT(YEAR FROM date) = (
                SELECT MIN(EXTRACT(YEAR FROM date))
                FROM food_prices
            )
        ),
        2
    ) AS start_price,

    -- Average price in the last year
    ROUND(
        AVG(price) FILTER (
            WHERE EXTRACT(YEAR FROM date) = (
                SELECT MAX(EXTRACT(YEAR FROM date))
                FROM food_prices
            )
        ),
        2
    ) AS end_price,

    -- Percentage change between first and last year
    ROUND(
        (
            (
                AVG(price) FILTER (
                    WHERE EXTRACT(YEAR FROM date) = (
                        SELECT MAX(EXTRACT(YEAR FROM date))
                        FROM food_prices
                    )
                )
                -
                AVG(price) FILTER (
                    WHERE EXTRACT(YEAR FROM date) = (
                        SELECT MIN(EXTRACT(YEAR FROM date))
                        FROM food_prices
                    )
                )
            )
            /
            NULLIF(
                AVG(price) FILTER (
                    WHERE EXTRACT(YEAR FROM date) = (
                        SELECT MIN(EXTRACT(YEAR FROM date))
                        FROM food_prices
                    )
                ),
                0
            )
        ) * 100,
        2
    ) AS percentage_change

FROM food_prices

GROUP BY commodity

-- Only include commodities with prices in both years
HAVING
    AVG(price) FILTER (
        WHERE EXTRACT(YEAR FROM date) = (
            SELECT MIN(EXTRACT(YEAR FROM date))
            FROM food_prices
        )
    ) IS NOT NULL

    AND

    AVG(price) FILTER (
        WHERE EXTRACT(YEAR FROM date) = (
            SELECT MAX(EXTRACT(YEAR FROM date))
            FROM food_prices
        )
    ) IS NOT NULL

ORDER BY percentage_change DESC
LIMIT 10;


-- 2.2 Compare average prices by category and country

-- The table has no region column, so countryiso3 is used instead.
WITH country_category_prices AS (
    SELECT
        category,
        countryiso3,
        AVG(price) AS average_price
    FROM food_prices
    GROUP BY
        category,
        countryiso3
)

SELECT
    category,
    countryiso3,
    ROUND(average_price, 2) AS average_price,

    -- Rank countries within each category
    RANK() OVER (
        PARTITION BY category
        ORDER BY average_price DESC
    ) AS country_rank

FROM country_category_prices

ORDER BY
    category,
    country_rank;


-- 2.3 Measure price volatility for each commodity
SELECT
    commodity,
    COUNT(*) AS price_records,

    -- Standard deviation shows price variation
    ROUND(STDDEV_SAMP(price), 2) AS price_standard_deviation

FROM food_prices
GROUP BY commodity

-- Need more than one record to calculate standard deviation
HAVING COUNT(*) > 1

ORDER BY price_standard_deviation DESC;


-- 2.4 Affordability trend for Nigeria
WITH yearly_prices AS (
    SELECT
        EXTRACT(YEAR FROM date)::int AS year,
        AVG(price) AS average_price
    FROM food_prices
    WHERE countryiso3 = 'NGA'
    GROUP BY EXTRACT(YEAR FROM date)
),

-- Get the previous year's average price
yearly_comparison AS (
    SELECT
        year,
        average_price,
        LAG(average_price) OVER (
            ORDER BY year
        ) AS previous_year_price
    FROM yearly_prices
)

SELECT
    year,
    ROUND(average_price, 2) AS average_price,
    ROUND(previous_year_price, 2) AS previous_year_price,

    -- Calculate year-over-year percentage change
    ROUND(
        (
            (average_price - previous_year_price)
            / NULLIF(previous_year_price, 0)
        ) * 100,
        2
    ) AS yoy_percentage_change

FROM yearly_comparison
ORDER BY year;
