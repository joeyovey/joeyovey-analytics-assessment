-- DATA QUALITY AUDIT

-- 1. How many total records are in the table?
    SELECT COUNT(*) AS total_records
    FROM food_prices;

-- 2. Which columns have null values, and how many nulls does each have?
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

    -- 2.1 admin1, with 138 nulls vaues
    -- 2.2 admin2, with 138 nulls values
    -- 2.3 latitude, with 138 nulls values
    -- 2.4 longitude, with 138 nulls values
    -- 2.5 price, with 757 nulls values

-- 3. Are there duplicate rows? Define what "duplicate" means for this dataset and justify it.
    SELECT
        countryiso3, date, market, commodity, unit, currency, price,
        COUNT(*) AS duplicate_count
    FROM food_prices
    GROUP BY
         countryiso3, date, market, commodity, unit, currency, price,
    HAVING COUNT(*) > 1
    ORDER BY duplicate_count DESC;

    -- Yes, there are duplicate rows. A duplicate is defined as a row that has the same values for all columns. 
    -- This is justifiable because, if all attributes of two records are identical, they represent the same data point 
    -- and this can be considered duplicates.

-- 1.4 What is the date range of the data? Are there any gaps in the time series?
    SELECT MIN(date) AS start_date, MAX(date) AS end_date
    FROM food_prices;
    -- The date range of the data is from 2000-01-01 to 2023-12-31. 

-- 1.5  Which (country, commodity) pairs have the most price records?
    SELECT countryiso3, commodity, COUNT(*) AS record_count
    FROM food_prices
    GROUP BY countryiso3, commodity
    ORDER BY record_count DESC
    LIMIT 5;
    -- 