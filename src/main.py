import boto3
import botocore
import os
import sys
import time
import zipfile

S3_BUCKET = os.environ.get('NONA_S3_BUCKET', None)
S3_ENDPOINT = os.environ.get('NONA_S3_ENDPOINT', None)
STAGE = os.environ.get('NONA_STAGE', 'development')
VERSION = os.environ.get('NONA_BACKUP_VERSION', 'latest')
DATA_PATH = os.environ.get('NONA_DATA_PATH', '/data')


if not S3_BUCKET:
    sys.exit(1)

s3 = boto3.resource('s3')
if S3_ENDPOINT:
    s3 = boto3.resource('s3', endpoint_url=S3_ENDPOINT)

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

def zipit(dir_list, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dir in dir_list:
        zipdir(dir, zipf)
    zipf.close()

def push_backup():
    print('Started tear down')
    backup_list = ['/data/{}'.format(dir) for dir in next(os.walk('/data'))[1]]

    # Zip the directories
    backup_name = 'data_backup_{}.zip'.format(int(time.time()))
    backup_local_path = '/tmp/{}'.format(backup_name)
    zipit(backup_list, backup_local_path)

    # Upload to S3
    s3.meta.client.upload_file(
        backup_local_path, 
        S3_BUCKET, 
        'backup/{}/{}'.format(STAGE, backup_name)
    )
    s3.meta.client.upload_file(
        backup_local_path, 
        S3_BUCKET, 
        'backup/{}/latest.zip'.format(STAGE)
    )
    print('Backed up to s3')

def main():
    push_backup()

if __name__ == "__main__":
    main()
