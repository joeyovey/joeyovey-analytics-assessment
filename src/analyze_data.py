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

    # Line chart showing price over time for at least 3 commodities in one country
    print("\nCreating price trend chart...")

    country_df = df[
        df["countryiso3"] == "NGA"
    ].copy()

    top_commodities = (
        country_df["commodity"]
        .value_counts()
        .head(3)
        .index
        .tolist()
    )

    trend_df = (
        country_df[
            country_df["commodity"].isin(
                top_commodities
            )
        ]
        .groupby(
            ["date", "commodity"]
        )["price"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(14, 8))

    for commodity in top_commodities:

        commodity_data = trend_df[
            trend_df["commodity"] == commodity
        ]

        plt.plot(
            commodity_data["date"],
            commodity_data["price"],
            label=commodity
        )

    plt.xlabel("Date")
    plt.ylabel("Average Price")
    plt.title(
        "Food Price Trend for Three Commodities in Nigeria"
    )

    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        f"{OUTPUT_DIR}/price_trend.png",
        dpi=200
    )

    plt.close()

    print("Saved price_trend.png")

    # Chart comparing price volatility across commodities. Commodities that has prices that vary the most.
    print("\nCreating volatility chart...")

    volatility = (
        df.groupby("commodity")["price"]
        .agg(
            price_std="std",
            record_count="count"
        )
        .reset_index()
    )

    volatility = volatility[
        volatility["record_count"] > 1
    ]

    volatility = (
        volatility
        .sort_values(
            "price_std",
            ascending=False
        )
        .head(15)
    )

    plt.figure(figsize=(12, 8))

    plt.barh(
        volatility["commodity"],
        volatility["price_std"]
    )

    plt.xlabel("Price Standard Deviation")
    plt.ylabel("Commodity")
    plt.title(
        "Price Volatility Across Commodities"
    )

    plt.gca().invert_yaxis()
    plt.tight_layout()

    plt.savefig(
        f"{OUTPUT_DIR}/volatility.png",
        dpi=200
    )

    plt.close()

    print("Saved volatility.png")

    # 3–5 bullet points summarising  most interesting findings
    print("\nCreating findings report...")

    nigeria_average = (
        df.loc[
            df["countryiso3"] == "NGA",
            "price"
        ].mean()
    )

    highest_volatility = (
        volatility.iloc[0]["commodity"]
        if not volatility.empty 
        else "Not available"
    )

    findings = f"""
- The dataset currently contains data from {df["date"].dt.year.min()} to {df["date"].dt.year.max()}. Because only one year is available, a true year-over-year price movement cannot be calculated.
- The average recorded food price for Nigeria in the available dataset is {nigeria_average:,.2f}.
- The commodity with the highest observed price standard deviation is {highest_volatility}, indicating the largest price variation among the commodities analysed.
- The dataset contains {len(df):,} usable price records after cleaning, with {rows_dropped:,} rows removed during the analysis cleaning step.   
"""

    with open(
        f"{OUTPUT_DIR}/findings.md",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(findings)

    print("Saved findings.md")


if __name__ == "__main__":
    main()