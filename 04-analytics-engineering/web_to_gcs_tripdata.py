import io
import os
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage

"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change the default value of BUCKET
"""

# Base URL for data download
init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'

# Default GCS Bucket (Change as needed)
BUCKET = os.environ.get("GCP_GCS_BUCKET", "taxi-rides-ny-md4")

def upload_to_gcs(bucket, object_name, local_file):
    """
    Uploads a file to Google Cloud Storage.
    """
    CREDENTIALS_FILE = "gcs.json"  
    client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
    bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

def web_to_gcs(year, service):
    for i in range(12):
        
        # Format the month with two digits
        month = f"{i+1:02d}"

        # CSV file name
        file_name = f"{service}_tripdata_{year}-{month}.csv.gz"

        # Download the file
        request_url = f"{init_url}{service}/{file_name}"
        r = requests.get(request_url)
        open(file_name, 'wb').write(r.content)
        print(f"Downloaded: {file_name}")

        # Define column data types explicitly to avoid schema mismatches
        column_types = {
            "VendorID": "string",
            "tpep_pickup_datetime": "string",  # Read as string first, then convert to TIMESTAMP
            "tpep_dropoff_datetime": "string",
            "passenger_count": "Int64",  
            "trip_distance": "float64",
            #"trip_type": "Int64", # remove for yellow
            "RatecodeID": "string",
            "store_and_fwd_flag": "string",
            "PULocationID": "string",
            "DOLocationID": "string",
            "payment_type": "Int64",
            "fare_amount": "float64",
            "extra": "float64",
            "mta_tax": "float64",
            "tip_amount": "float64",
            "tolls_amount": "float64",
            "improvement_surcharge": "float64",
            "total_amount": "float64",
            "congestion_surcharge": "float64",
            #"ehail_fee": "float64" # remove for yellow
        }

        # Read CSV with explicit dtypes
        df = pd.read_csv(file_name, compression='gzip', dtype=column_types, low_memory=False)

        # Convert datetime columns to Pandas datetime format (which translates to TIMESTAMP in Parquet)
        #df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors='coerce')
        #df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors='coerce')

        # Fill NaN values in passenger_count (BigQuery does not allow NULLs in FLOAT64)
        df["passenger_count"] = df["passenger_count"].fillna(0).astype("float64")

        # Convert the DataFrame to a PyArrow Table with the correct schema
        table = pa.Table.from_pandas(df, schema=pa.schema([
            pa.field("VendorID", pa.string()),
            pa.field("tpep_pickup_datetime", pa.string()),  # ✅ Ensure TIMESTAMP type in Parquet
            pa.field("tpep_dropoff_datetime", pa.string()),  # ✅ Ensure TIMESTAMP type in Parquet
            pa.field("passenger_count", pa.int64()),
            pa.field("trip_distance", pa.float64()),
            #pa.field("trip_type", pa.int64()), # remove for yellow
            pa.field("RatecodeID", pa.string()),
            pa.field("store_and_fwd_flag", pa.string()),
            pa.field("PULocationID", pa.string()),
            pa.field("DOLocationID", pa.string()),
            pa.field("payment_type", pa.int64()),
            pa.field("fare_amount", pa.float64()),
            pa.field("extra", pa.float64()),
            pa.field("mta_tax", pa.float64()),
            pa.field("tip_amount", pa.float64()),
            pa.field("tolls_amount", pa.float64()),
            pa.field("improvement_surcharge", pa.float64()),
            pa.field("total_amount", pa.float64()),
            pa.field("congestion_surcharge", pa.float64()),
            #pa.field("ehail_fee", pa.float64()) # remove for yellow 
        ]))

        # Save as Parquet with correct schema
        file_name = file_name.replace('.csv.gz', '.parquet')
        pq.write_table(table, file_name)
        print(f"Converted to Parquet: {file_name}")

        # Upload to GCS
        upload_to_gcs(BUCKET, f"{service}/{file_name}", file_name)
        print(f"Uploaded to GCS: {service}/{file_name}")

# web_to_gcs('2019', 'green')
# web_to_gcs('2020', 'green')
# web_to_gcs('2019', 'yellow')
web_to_gcs('2020', 'yellow')
