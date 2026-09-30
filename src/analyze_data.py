import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


DATABASE_URL = (
    "postgresql+psycopg2://"
    "postgres:postgres@postgres:5432/assessment_db"
)

OUTPUT_DIR = "outputs"

def main():
    print("Starting analysis...")

    engine = create_engine(DATABASE_URL)

    query = """
        SELECT *
        FROM food_prices;
    """

    df = pd.read_sql(query, engine)

    print(f"Rows loaded: {len(df)}")
    print(f"Columns loaded: {len(df.columns)}")

    print("\nChecking data quality...")

    rows_before = len(df)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "market_id",
        "latitude",
        "longitude",
        "commodity_id",
        "price",
        "usdprice"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    required_columns = [
        "countryiso3",
        "date",
        "market",
        "market_id",
        "category",
        "commodity",
        "commodity_id",
        "unit",
        "currency",
        "price"
    ]

    df = df.dropna(
        subset=required_columns
    )

    rows_after = len(df)
    rows_dropped = rows_before - rows_after

    print(f"Rows before cleaning: {rows_before}")
    print(f"Rows dropped: {rows_dropped}")
    print(f"Rows remaining: {rows_after}")


if __name__ == "__main__":
    main()