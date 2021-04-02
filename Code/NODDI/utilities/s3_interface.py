import boto3
import boto
import os
import argparse
import logging
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3Transfer

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Interface:

	def __init__(self, public_key, secret_key, bucket_pattern):

		self.public_key = public_key
		self.secret_key = secret_key
		self.bucket_pattern = bucket_pattern

		self.transfer = S3Transfer(
				boto3.client('s3', 'us-east-1',
					aws_access_key_id=self.public_key,
					aws_secret_access_key=self.secret_key
				)
			  )
		self.s3_client = boto3.client('s3', 'us-east-1',
					aws_access_key_id=self.public_key,
					aws_secret_access_key=self.secret_key
				)
		self.s3 = boto.connect_s3(
				aws_access_key_id=self.public_key,
				aws_secret_access_key=self.secret_key
			  )	
		for key in self.s3.get_all_buckets():
			if key.name.find(self.bucket_pattern) != -1:
				self.s3_bucket = key
				self.bucket_name = key.name
				break



	def upload_file(self, file_path, destination_path):
	
		# based on the file path of the local directory, the bucket name found 
		# through th bucket_pattern, and the actual file from the file path
		try:
			logging.info(f"Uploading file ({file_path}) to bucket {self.bucket_name} under this path: {destination_path}")
			self.transfer.upload_file(file_path, self.bucket_name, destination_path)
		except ClientError as e:
			logging.error(e)
			return False
		return True

	def upload_files(self, file_path, destination_path):
	
		# based on the file path of the local directory, the bucket name found 
		# through th bucket_pattern, and the actual file from the file path
		try:
			logging.info(f"Uploading file ({file_path}) to bucket {self.bucket_name} under this path: {destination_path}")
			for (sourceDir, dirname, filename) in os.walk(file_path):
				for file in filename:
					if file[0] != '.':
						full_path = os.path.join(sourceDir, file)
						full_distin_path = os.path.join(destination_path, os.path.join(sourceDir[len(file_path)+1:], file))
						logger.info(full_path)
						logger.info(full_distin_path)
						self.transfer.upload_file(full_path, self.bucket_name, full_distin_path)
		except ClientError as e:
			logging.error(e)
			return False
		return True

	def download_file(self, object_name, file_name):

		try:
			logging.info(f"Downloading subject with filename {file_name}")
			self.transfer.download_file(self.bucket_name, object_name, file_name)
		except ClientError as e:
			logging.error(e)
			return False
		return True

	def download_files(self, object_name, destination_file_name):

		if not os.path.exists(destination_file_name):
			os.makedirs(destination_file_name)
	
		try:
			logging.info(f"Downloading files")
			print(f"object name = {object_name}")
			print(f"bucket name = {self.bucket_name}")
			object_list = self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=object_name)['Contents']
			print(object_list)
			for obj_dict in object_list:
				if obj_dict['Size'] != 0:
					path_to, filename = os.path.split(obj_dict['Key'])
					path_to, one_up = os.path.split(path_to)
					_, two_up = os.path.split(path_to)
					destination_directory = os.path.join(destination_file_name, two_up, one_up)
					if os.path.exists(os.path.join(destination_directory, filename)):
						continue	
					os.makedirs(destination_directory, exist_ok=True)
					print(obj_dict)
					key = obj_dict['Key']
					print(f"base name = {os.path.basename(key)}")
					logging.info(f"Downloading {key}")
					# self.transfer.download_file(self.bucket_name, key,
					# 				os.path.join(destination_file_name,
					# 						os.path.join(two_up, one_up, filename)
					# 				)
					# )
		except ClientError as e:
			logging.error(e)
			return False
		return True	
			
def main():
	logging.info("started")
	description = """
                    upload or download files from S3 bucket
                    """
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('-u', '--upload', action='store_true', help="upload option")
	parser.add_argument('-v', '--download', action='store_true', help="download option")

	parser.add_argument('-b', '--bucket', type=str, help="s3 bucket")
	parser.add_argument('-p', '--path', type=str, help="local folder directory")
	parser.add_argument('-d', '--distination', type=str, help="S3 folder directory")
	
	args = parser.parse_args()

	s3 = S3Interface(os.environ['AWSAccessKeyId'], os.environ['AWSSecretKey'], args.bucket)
	if args.upload:
		s3.upload_files(args.path, args.distination)
	elif args.download:
		s3.download_files(args.distination, args.path)
main()