import pandas as pd
from sqlalchemy import create_engine, text

CSV_FILE_PATH = "data/food_prices.csv"

DATABASE_URL = (
    "postgresql+psycopg2://"
    "postgres:postgres@postgres:5432/assessment_db"
)


def main():

    # Create database engine
    engine = create_engine(DATABASE_URL)

    # Load data from CSV file
    print("Reading dataset...")
    df = pd.read_csv(CSV_FILE_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns found: {len(df.columns)}")

    # Convert the 'date' column to datetime format
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Convert numeric columns
    numeric_columns = [
        "market_id",
        "latitude",
        "longitude",
        "price",
        "commodity_id",
        "usdprice"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Count invalid values
    invalid_dates = df["date"].isna().sum()
    invalid_prices = df["price"].isna().sum()

    print(f"Invalid dates: {invalid_dates}")
    print(f"Invalid prices: {invalid_prices}")

    # Remove rows without valid required values
    before = len(df)

    df = df.dropna(
        subset=[
            "countryiso3",
            "date",
            "price",
            "market_id",
            "market",
            "commodity_id",
            "commodity",
            "unit",
            "currency",
            "category"
        ]
    )

    skipped = before - len(df)

    print(f"Rows skipped: {skipped}")
    print(f"Rows remaining: {len(df)}")

    # Connect to PostgreSQL
    print("\nConnecting to PostgreSQL...")

    # Create table
    create_table = """
    CREATE TABLE IF NOT EXISTS food_prices (
        id SERIAL PRIMARY KEY,
        countryiso3 VARCHAR(3) NOT NULL,
        date DATE NOT NULL,
        admin1 VARCHAR(255),
        admin2 VARCHAR(255),
        market VARCHAR(255) NOT NULL,
        market_id INTEGER NOT NULL,
        latitude NUMERIC(9,6),
        longitude NUMERIC(9,6),
        category VARCHAR(255) NOT NULL,
        commodity VARCHAR(255) NOT NULL,
        commodity_id INTEGER NOT NULL,
        unit VARCHAR(100) NOT NULL,
        priceflag VARCHAR(50),
        pricetype VARCHAR(50),
        currency VARCHAR(10) NOT NULL,
        price NUMERIC(18,4) NOT NULL,
        usdprice NUMERIC(18,4)
    )
    """

    # Create/reset the table
    with engine.begin() as connection:

        connection.execute(
            text("DROP TABLE IF EXISTS food_prices")
        )

        connection.execute(
            text(create_table)
        )

    print("Table 'food_prices' created successfully.")

    # Load data into PostgreSQL
    print("Loading data into PostgreSQL...")

    df.to_sql(
        "food_prices",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Data loaded successfully.")

    # Create indexes
    print("Creating indexes...")

    with engine.begin() as connection:

        connection.execute(
            text(
                "CREATE INDEX idx_countryiso3 "
                "ON food_prices (countryiso3)"
            )
        )

        connection.execute(
            text(
                "CREATE INDEX idx_date "
                "ON food_prices (date)"
            )
        )

        connection.execute(
            text(
                "CREATE INDEX idx_commodity_id "
                "ON food_prices (commodity_id)"
            )
        )

    print("Indexes created successfully.")

    # Check number of rows
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT COUNT(*) FROM food_prices")
        )

        count = result.scalar()

    print(f"Rows in database: {count}")


if __name__ == "__main__":
    main()