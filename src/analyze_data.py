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

    print("\nCreating summary statistics...")

    numeric_df = df.select_dtypes(
        include=np.number
    )

    summary_stats = pd.DataFrame({
        "min": numeric_df.min(),
        "max": numeric_df.max(),
        "mean": numeric_df.mean(),
        "median": numeric_df.median(),
        "std": numeric_df.std()
    })

    summary_stats.to_csv(
        f"{OUTPUT_DIR}/summary_stats.csv"
    )

    print("Saved summary_stats.csv")

    print("\nCreating top movers chart...")

    yearly_prices = (
        df.assign(
            year=df["date"].dt.year
        )
        .groupby(["commodity", "year"])["price"]
        .mean()
        .reset_index()
    )

    years = sorted(
        yearly_prices["year"].unique()
    )

    if len(years) >= 2:

        first_year = years[0]
        last_year = years[-1]

        start_prices = (
            yearly_prices[
                yearly_prices["year"] == first_year
            ]
            .set_index("commodity")["price"]
        )

        end_prices = (
            yearly_prices[
                yearly_prices["year"] == last_year
            ]
            .set_index("commodity")["price"]
        )

        movers = pd.DataFrame({
            "start_price": start_prices,
            "end_price": end_prices
        }).dropna()

        movers["percentage_change"] = (
            (movers["end_price"] - movers["start_price"])
            / movers["start_price"].replace(0, np.nan)
        ) * 100

        movers = (
            movers
            .sort_values(
                "percentage_change",
                ascending=False
            )
            .head(10)
        )

        plt.figure(figsize=(12, 8))

        plt.barh(
            movers.index,
            movers["percentage_change"]
        )

        plt.xlabel("Percentage Change (%)")
        plt.ylabel("Commodity")
        plt.title(
            f"Top 10 Commodity Price Movers "
            f"({first_year}–{last_year})"
        )

        plt.gca().invert_yaxis()
        plt.tight_layout()

        plt.savefig(
            f"{OUTPUT_DIR}/top_movers.png",
            dpi=200
        )

        plt.close()

    else:

        plt.figure(figsize=(12, 8))

        plt.text(
            0.5,
            0.5,
            "Only one year is available.\n"
            "Year-over-year price movement cannot be calculated.",
            ha="center",
            va="center",
            fontsize=20
        )

        plt.axis("off")
        plt.title("Top Movers — Data Limitation")

        plt.tight_layout()

        plt.savefig(
            f"{OUTPUT_DIR}/top_movers.png",
            dpi=200
        )

        plt.close()

    print("Saved top_movers.png")


if __name__ == "__main__":
    main()