-- DATA QUALITY AUDIT

-- 1. How many total records are in the table?
    SELECT COUNT(*) AS total_records
    FROM food_prices;

-- 2. Which columns have null values, and how many nulls does each have?
    -- 2.1 admin1, with 138 nulls vaues
    -- 2.2 admin2, with 138 nulls values
    -- 2.3 latitude, with 138 nulls values
    -- 2.4 longitude, with 138 nulls values
    -- 2.5 price, with 757 nulls values

-- 3. Are there duplicate rows? Define what "duplicate" means for this dataset and justify it.
    -- Yes, there are duplicate rows. A duplicate is defined as a row that has the same values for all columns. 
    -- This is justifiable because, if all attributes of two records are identical, they represent the same data point 
    -- and this can be considered duplicates.
