from dmipy.hcp_interface import downloader_aws
import logging
import argparse
import os
from s3_interface import S3Interface

s3 = S3Interface(os.environ['AWS_S3_KEY'], os.environ['AWS_S3_PRIVATE_KEY'], 'cs-sjsu-noddi-patient-files')
logger = logging.getLogger(__name__)

def make_hcp_interface(public_key, secret_key):

        hcp_interface = downloader_aws.HCPInterface(
                                your_aws_public_key=public_key,
                                your_aws_private_key=private_key
                        )
        return hcp_interface


def upload_files(interface, file_path, destination_file_path):

        if interface.upload_files(file_path, destination_file_path):
            return True
        else:
            return False

	
if __name__ == "__main__":
	
        parser = argparse.ArgumentParser(description='Uploader interface')
        parser.add_argument('--file_path', '-f', type=str, help='the path pointing to the file you wish to upload')
        parser.add_argument('--destination_path', '-d', type=str, help='the path on the s3 bucket you wish to place the file')
        parser.add_argument('--bucket_name', '-b', type=str, help='the bucket name you wish to place the file in')

        args = parser.parse_args()

        try:
            s3 = S3Interface(os.environ['AWS_S3_KEY'],
                             os.environ['AWS_S3_PRIVATE_KEY'],
                             args.bucket_name)
            upload_files(s3, args.file_path, args.destination_path)
        except:
            logger.info("failed upload")

        
		
	
