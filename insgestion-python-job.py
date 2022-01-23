import os
import argparse

import pandas as pd
from sqlalchemy import create_engine

def main(args):
    # setup
    ## args
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    db = args.db
    table = args.table
    url = args.url
    csv_file = 'data.csv'
    iteration_count = 1
    
    ## connection with db
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # download the data
    os.system(f"wget {url} -O {csv_file}")
    
    # read data on chunks
    df_iterator = pd.read_csv(csv_file, iterator=True, chunksize=100000)

    # create table and add first data
    df = next(df_iterator)

    ## fix date format
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    ## create table
    try:
        df.head(0).to_sql(name=table, con=engine)
        print('Table created')
    except:
        print("Table already exist")

    ## add first iteration
    df.to_sql(name=table, con=engine, if_exists='append')
    print(f'Iteration number {iteration_count} inserted')

    # add other iterations

    while True:
        try:
            df = next(df_iterator)
        except:
            break

        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        iteration_count += 1
        
        df.to_sql(name=table, con=engine, if_exists='append')
        
        print(f'Iteration number {iteration_count} inserted')
    
    print('Insgestion completed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--db')
    parser.add_argument('--table')
    parser.add_argument('--url')

    args = parser.parse_args()

    main(args)
