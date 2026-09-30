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


if __name__ == "__main__":
    main()