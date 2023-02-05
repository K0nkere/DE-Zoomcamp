#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os

import pyarrow as pa 
from pyarrow.parquet import ParquetFile

# import psycopg2
from sqlalchemy import create_engine

from datetime import datetime

from pathlib import Path

from time import time


# In[ ]:


parent = os.path.split("__filename__")[0]
os.path.split(parent)[0]


# In[ ]:


pf = ParquetFile('../ny-taxi-data/yellow_tripdata_2021-01.parquet') 
dataset_nrows = next(pf.iter_batches(batch_size = 100)) 
data = pa.Table.from_batches([dataset_nrows]).to_pandas()
data


# In[ ]:


# data["tpep_pickup_datetime"] = data["tpep_pickup_datetime"].apply(lambda x: datetime.strftime(x, "%y-%m-%d %H:%M:%S"))
# data["tpep_pickup_datetime"] = data["tpep_pickup_datetime"].apply(lambda x: datetime.strftime(x, "%y-%m-%d %H:%M:%S"))


# In[23]:


engine = create_engine("postgresql://root:root@localhost/ny_taxi")
engine.connect()


# In[24]:


print(pd.io.sql.get_schema(data, name="yellow_taxi_data", con=engine))


# In[ ]:


query = """
SELECT *
FROM pg_catalog.pg_tables
WHERE schemaname != 'pg_catalog' AND
    schemaname != 'information_schema';
"""

pd.read_sql(query, con=engine)


# In[25]:


df_head = data.head(0)
df_head.to_sql(name="yellow_taxi_tripdata", con=engine, if_exists='replace')


# In[28]:


pf = ParquetFile('../ny-taxi-data/yellow_tripdata_2021-01.parquet') 

batch_size = 100000
pf_iter = pf.iter_batches(batch_size = batch_size)

while batch_size == 100000  :
    t_start = time()
    dataset_nrows = next(pf_iter)
    data = pa.Table.from_batches([dataset_nrows]).to_pandas()

    data["tpep_pickup_datetime"] = pd.to_datetime(data["tpep_pickup_datetime"])
    data["tpep_dropoff_datetime"] = pd.to_datetime(data["tpep_dropoff_datetime"])

    data.to_sql(name="yellow_taxi_tripdata", con=engine, if_exists='append')

    batch_size = dataset_nrows.num_rows

    t_end = time()

    print("...inserting data %.2f" %(t_end - t_start))


# In[27]:


dataset_nrows.num_rows


# In[16]:




