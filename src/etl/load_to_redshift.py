"""Load a DataFrame to Redshift via COPY from S3."""
import os
import boto3
import pandas as pd


def upload_parquet_to_s3(df: pd.DataFrame, bucket: str, key: str) -> str:
    s3 = boto3.client("s3")
    buf = "/tmp/temp.parquet"
    df.to_parquet(buf, index=False)
    s3.upload_file(buf, bucket, key)
    return f"s3://{bucket}/{key}"


def copy_to_redshift(s3_uri: str, table: str):
    import redshift_connector
    conn = redshift_connector.connect(
        host=os.environ["REDSHIFT_HOST"],
        database=os.environ["REDSHIFT_DB"],
        user=os.environ["REDSHIFT_USER"],
        password=os.environ["REDSHIFT_PASSWORD"],
    )
    cur = conn.cursor()
    cur.execute(f"""
        COPY {table} FROM '{s3_uri}'
        IAM_ROLE '{os.environ["REDSHIFT_IAM_ROLE"]}'
        FORMAT AS PARQUET;
    """)
    conn.commit()
    cur.close(); conn.close()
