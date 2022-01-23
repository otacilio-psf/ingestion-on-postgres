import argparse
import requests

from pyspark.sql import SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import TimestampType

def main(args):
    # setup
    ## args
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    db = args.db
    db_url = f'jdbc:postgresql://{host}:{port}/{db}'
    table = args.table
    url = args.url
    csv_file = 'data.csv'
    

    # download the data
    print("Dowloading data")
    session = requests.Session()
    r = session.get(url, stream=True)
    if r.status_code == requests.codes.OK:
        with open(f"./{csv_file}", "wb") as new_file:
            for part in r.iter_content(chunk_size=1024*1024*5):
                new_file.write(part)
    else:
        r.raise_for_status()
    
    # Spark session
    spark = SparkSession.builder.appName("ingestion-on-pg").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    csv_options = {
        "header": "true",
        "sep": ",",
        "inferSchema": "true"
    }

    df = (spark.read.format("csv")
                    .options(**csv_options)
                    .load(csv_file))

    ## fix date format
    df = (df.withColumn('tpep_pickup_datetime', sf.col('tpep_pickup_datetime').cast(TimestampType()))
            .withColumn('tpep_dropoff_datetime', sf.col('tpep_dropoff_datetime').cast(TimestampType())))

    table_options = {
        "url": db_url,
        "dbtable": table,
        "username": user,
        "password": password,
        "driver": "org.postgresql.Driver"
    }

    print("Writing data")
    
    (df.write
    .format("jdbc")
    .mode("append")
    .options(**table_options)
    .save())
    
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
