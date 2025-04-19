from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

    def exists(self, name):
        try:
            self.connection.meta.client.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except Exception as e:
            print(f"Error checking if {name} exists in bucket {self.bucket_name}: {e}")
            return False