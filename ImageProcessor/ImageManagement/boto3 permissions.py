import boto3

s3 = boto3.client('s3')
try:
    response = s3.list_objects_v2(
        Bucket='imageprocessingbucket2',
        Prefix='media/Images/'
    )
    for obj in response.get('Contents', []):
        print(obj['Key'])
except Exception as e:
    print(f"Error: {str(e)}")