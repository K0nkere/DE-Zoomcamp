FROM python:3.9-slim-buster

RUN apt-get update
RUN apt install -y wget

RUN pip install -U pip
RUN pip install pandas pyarrow psycopg-binary psycopg2-binary sqlalchemy
WORKDIR /app

COPY upload-data.py upload-data.py

ENTRYPOINT [ "python",  "upload-data.py" ]