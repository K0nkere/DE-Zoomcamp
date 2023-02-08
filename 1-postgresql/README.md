### Postgres running

docker run -itd \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_pgdata:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name ny-taxi-database \
    postgres:13

pgcli -h localhost -p 5432 -u root -d ny_taxi

### pgAdmin
image - docker pull dpage/pgadmin4

docker run -itd \
    -p 8080:80 \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com"\
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    --network=pg-network \
    --name pgAdmin-server \
    dpage/pgadmin4

### Docker Network create

docker network create pg-network

pass=root

python upload-data.py \
    --user=root\
    --password=${pass}\
    --server=localhost\
    --port=5432 \
    --database=ny_taxi \
    --table=yellow_taxi_tripdata \
    --data_url=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet \
    --output_file=output-taxi-data.parquet\
    --preprocess=yes


### Docker image run
docker run -it --network=pg-network \
    upload-data:v01 \
        --user=root\
        --password=${pass}\
        --server=ny-taxi-database\
        --port=5432 \
        --database=ny_taxi \
        --table=yellow_taxi_tripdata \
        --data_url=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet \
        --output_file=output-taxi-data.parquet \
        --preprocess=yes

#### for downloading from local http server
docker run -it --network=pg-network \
    upload-data:v01 \
    --user=root\
    --password=${pass}\
    --server=ny-taxi-database\
    --port=5432 \
    --database=ny_taxi \
    --table=yellow_taxi_tripdata \
    --data_url=http://51.250.31.202:8000/ny-taxi-data/yellow_tripdata_2021-01.parquet \
    --output_file=output-taxi-data.parquet \
    --preprocess=yes

#### for injesting data while services are launched in docker-compose
docker run -it --network=de-zoomcamp_pg-network\
    upload-data:v01 \
        --user=root\
        --password=${pass}\
        --server=ny-taxi-database\
        --port=5432 \
        --database=ny_taxi \
        --table=yellow_taxi_tripdata \
        --data_url=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet \
        --output_file=output-taxi-data.parquet \
        --preprocess=yes

#### for taxi zones table
python upload-data.py \
        --user=root\
        --password=${pass}\
        --server=localhost\
        --port=5432 \
        --database=ny_taxi \
        --table=taxi_zone_lookup \
        --data_url=https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv \
        --output_file=output-taxi-zones.csv \
        --preprocess=no

docker run -it --network=de-zoomcamp_pg-network\
    upload-data:v01 \
        --user=root\
        --password=${pass}\
        --server=ny-taxi-database\
        --port=5432 \
        --database=ny_taxi \
        --table=taxi_zone_lookup \
        --data_url=https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv \
        --output_file=output-taxi-zones.csv \
        --preprocess=no

### Dataset
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page