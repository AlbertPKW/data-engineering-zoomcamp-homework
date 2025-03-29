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
            "dispatching_base_num": "string",
            "pickup_datetime": "string",  # Read as string first, then convert to TIMESTAMP
            "dropOff_datetime": "string",
            "PUlocationID": "string",
            "DOlocationID": "string",
            "SR_Flag": "string",
            "Affiliated_base_number": "string"
        }

        # Read CSV with explicit dtypes
        df = pd.read_csv(file_name, compression='gzip', dtype=column_types, low_memory=False)

        # Convert datetime columns to Pandas datetime format (which translates to TIMESTAMP in Parquet)
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors='coerce')
        df["dropOff_datetime"] = pd.to_datetime(df["dropOff_datetime"], errors='coerce')

        # Convert the DataFrame to a PyArrow Table with the correct schema
        table = pa.Table.from_pandas(df, schema=pa.schema([
            pa.field("dispatching_base_num", pa.string()),
            pa.field("pickup_datetime", pa.timestamp('s')),  # ✅ Ensure TIMESTAMP type in Parquet
            pa.field("dropOff_datetime", pa.timestamp('s')),  # ✅ Ensure TIMESTAMP type in Parquet
            pa.field("PUlocationID", pa.string()),
            pa.field("DOlocationID", pa.string()),
            pa.field("SR_Flag", pa.string()),
            pa.field("Affiliated_base_number", pa.string())
        ]))

        # Save as Parquet with correct schema
        file_name = file_name.replace('.csv.gz', '.parquet')
        pq.write_table(table, file_name)
        print(f"Converted to Parquet: {file_name}")

        # Upload to GCS
        upload_to_gcs(BUCKET, f"{service}/{file_name}", file_name)
        print(f"Uploaded to GCS: {service}/{file_name}")


web_to_gcs('2019', 'fhv')