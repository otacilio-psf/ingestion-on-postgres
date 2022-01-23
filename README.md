# Data Ingestion

Ingest data with Python or Spark on Postgres

## Data
* https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf

## Database

* Postgres 14
* pgAdmin4 6.4 

```
docker-compose up -d
```

## Python Ingestion
### Local Ingestion
```
URL="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv"

python insgestion-python-job.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table=yellow_taxi_trips \
  --url=${URL}

rm data.csv
```

### Container Ingestion
Build image
```
docker build -t ingest-pg:1 -f Dockerfile-python .
```

Run Ingestion
```
URL="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-02.csv"

docker run -it \
  --network="${PWD##*/}"_pg-network \
  ingest-pg:1 \
    --user=root \
    --password=root \
    --host=postgres \
    --port=5432 \
    --db=ny_taxi \
    --table=yellow_taxi_trips \
    --url=${URL}
```

## Spark Ingestion
### Container Ingestion
Build image
```
mkdir -p jars
wget https://jdbc.postgresql.org/download/postgresql-42.3.1.jar -O ./jars/postgresql-42.3.1.jar

docker build -t ingest-spark-pg:1 -f Dockerfile-spark .

rm -r jars
```

Run Ingestion
```
URL="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-03.csv"

docker run -it \
  --network="${PWD##*/}"_pg-network \
  ingest-spark-pg:1 \
    --user=root \
    --password=root \
    --host=postgres \
    --port=5432 \
    --db=ny_taxi \
    --table=yellow_taxi_trips \
    --url=${URL}
```
