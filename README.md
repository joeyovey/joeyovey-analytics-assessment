# Junior Analytics Assessment

This project analyses global food price data using **Python, PostgreSQL, SQL, Pandas, and Docker**.

The analysis includes data quality checks, SQL analysis, summary statistics, price trends, price movements, and volatility.

## Data Decisions

* The dataset contains **245,288 records.**
* Dates and numeric columns were converted to the correct data types.
* No records were removed during the final Python cleaning step.
* Duplicate records were checked using country, date, market, commodity, unit, currency, and price.
* No duplicate observations were identified using this definition.
* Price values were checked for invalid values.
* The data covers **15 January 2026 to 15 September 2026.**

### Important Limitation

The dataset contains **only 2026 data.**
Because there is no previous year in the dataset, a true year-over-year comparison cannot be calculated.

The price trend analysis therefore focuses on the available 2026 period.

## Main Analysis
### 1. Data Quality
The data was checked for:
* Missing values
* Duplicate records
* Invalid dates
* Invalid prices
* Date range

### 2. Summary Statistics
`summary_stats.csv` contains:
* Minimum
* Maximum
* Mean
* Median
* Standard deviation for the numeric columns

### 3. Price Movement
`top_movers.png` shows commodity price movement.
Because only one year is available, the assessment's requested first-year versus last-year comparison is limited by the data.

### 4. Price Trend
`price_trend.png` shows the price trend of three commodities in Nigeria over the available period. Nigeria was used as the selected country for the trend.

### 5. Price Volatility
`volatility.png` compares commodities based on their price standard deviation.

### 6. Findings
`findings.md` contains the main findings from the analysis.

## How to Run the Project
### 1. Clone the repository
```bash
git clone https://github.com/joeyovey/joeyovey-analytics-assessment
cd joeyovey-analytics-assessment
```

### 2. Start Docker
```bash
docker compose up
```

### 3. Load the data
```bash
docker compose exec python python src/load_data.py
```

### 4. Run the Python analysis
```bash
docker compose exec python python src/analyze_data.py
```

### 5. Check the results
The generated files will be inside:
```text
outputs/
```

## Conclusion
This project demonstrates a basic data analysis workflow:
```text
Data > Cleaning > PostgreSQL > SQL Analysis > Python Analysis > Visualisation > Findings
```

The analysis uses the available data and clearly documents its limitations.
