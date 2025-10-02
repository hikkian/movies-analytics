import os
import pandas as pd
from config import engine

DATASETS_DIR = "datasets"

def import_data():
    tables = ["genres", "directors", "movies", "actors", "movie_actor", "users", "ratings"]
    for table in tables:
        csv_path = os.path.join(DATASETS_DIR, f"{table}.csv")
        df = pd.read_csv(csv_path)
        df.to_sql(table, engine, if_exists="append", index=False)
        print(f"✅ Loaded {len(df)} rows into '{table}'")

if __name__ == "__main__":
    import_data()