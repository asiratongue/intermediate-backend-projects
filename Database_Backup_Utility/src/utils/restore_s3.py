from urllib.parse import urlparse
import boto3
import os


def restore_s3(backups, extracted_backup):
    """
    Restore a backup from S3
    
    Parameters:
    backups (list): List of S3 URLs
    extracted_backup (str): Path where the extracted file should be saved
    """
    s3_url = backups[0]
    
    # Parse the S3 URL
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    object_key = parsed_url.path.lstrip('/')
    
    # Create a local temp file for the gzipped content
    local_file = os.path.join(extracted_backup, os.path.basename(s3_url))
    print(local_file)
    # Download the file from S3

    print(f"object key {object_key}")
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket_name, object_key, local_file)
    extracted_backup = local_file 
    
    return extracted_backup
