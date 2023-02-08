import pandas as pd
import os

import argparse
import pyarrow as pa 
from pathlib import Path
from pyarrow.parquet import ParquetFile

# import psycopg2 # no need to load under anaconda env
from sqlalchemy import create_engine
from time import time


def convert_to_parquet(output: Path) -> Path:
    data = pd.read_csv(output)
    output_path = os.path.join(os.path.split(output)[0], ".".join([os.path.split(output)[1].split(".")[0], "parquet"]))
    data.to_parquet(path=output_path, engine='pyarrow', index=False)

    return output_path


def upload_dataset(args):
    
    user = args.user
    password = args.password
    server = args.server
    port = args.port
    database = args.database
    table = args.table
    data_url = args.data_url
    output = args.output_file
    preprocess = args.preprocess

    os.system(f"wget {data_url} -O {output}")

    if output.endswith(".csv"):
        output = convert_to_parquet(output)
        print(f"{output}")

    batch_size = 100000
    pf = ParquetFile(f'{output}')

    dataset_nrows = next(pf.iter_batches(batch_size = 1)) 
    data = pa.Table.from_batches([dataset_nrows]).to_pandas()
    data.columns = data.columns.str.lower()

    engine = create_engine(f'postgresql://{user}:{password}@{server}:{port}/{database}')
    engine.connect()

    print(pd.io.sql.get_schema(data, name=f'{table}', con=engine))

    df_head = data.head(0)
    df_head.to_sql(name=f'{table}', con=engine, if_exists='replace')

    pf_iter = pf.iter_batches(batch_size = batch_size)

    while True  :
        try:
            t_start = time()
            dataset_nrows = next(pf_iter)

            data = pa.Table.from_batches([dataset_nrows]).to_pandas()
            data.columns = data.columns.str.lower()

            if preprocess=="yes":
                data["tpep_pickup_datetime"] = pd.to_datetime(data["tpep_pickup_datetime"])
                data["tpep_dropoff_datetime"] = pd.to_datetime(data["tpep_dropoff_datetime"])

            data.to_sql(name=f'{table}', con=engine, if_exists='append')

            t_end = time()

            print("...inserting data %.2f" %(t_end - t_start))

        except StopIteration:
            print (f"All data is uploaded to {table}")
            break


if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Ingest data to database",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-U", "--user", help="user")
    parser.add_argument("-P", "--password", help="password")
    parser.add_argument("-S", "--server", help="server url")
    parser.add_argument("--port", help="port to connect")
    parser.add_argument("-D", "--database", help="database")
    parser.add_argument("-T", "--table", help="name of inserting table")
    parser.add_argument("--data_url", help="url of data to download")
    parser.add_argument("--output_file", help="filename download output")
    parser.add_argument("--preprocess", help="yes/no preprocessiong of the data")

    args = parser.parse_args()
    
    print(args)
    
    upload_dataset(args)




